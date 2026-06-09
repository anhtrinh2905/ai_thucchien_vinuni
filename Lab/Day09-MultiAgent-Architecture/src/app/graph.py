from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph

from app.config import Settings
from app.data_access import ShoppingDataStore, build_data_tools
from app.prompts import (
    DATA_WORKER_SYSTEM,
    POLICY_WORKER_SYSTEM,
    RESPONSE_WORKER_PROMPT,
    SUPERVISOR_PROMPT,
)
from app.state import ShoppingState
from app.utils import (
    dump_json,
    extract_json_payload,
    get_last_ai_content,
    serialize_message,
    timestamp_utc,
)
from provider import get_chat_model
from rag.embeddings import SentenceTransformerEmbeddings
from rag.vector_store import ChromaPolicyStore


class ShoppingAssistant:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.load()
        self.llm = get_chat_model(self.settings)

        # Load data store
        self.data_store = ShoppingDataStore(self.settings.orders_path)
        self.data_tools = build_data_tools(self.data_store)

        # Load embedding model and vector store
        self.embedding_model = SentenceTransformerEmbeddings(
            self.settings.embedding_model_name
        )
        self.vector_store = ChromaPolicyStore(
            persist_directory=self.settings.chroma_dir,
            embedding_model=self.embedding_model,
        )
        self.vector_store.ensure_index(self.settings.policy_path)

        # Build search_policy tool (closure over self.vector_store)
        top_k = self.settings.top_k
        vs = self.vector_store

        @tool
        def search_policy(query: str) -> list:
            """Search the VinShop Demo policy knowledge base.
            Use this to find policy rules about returns, shipping, vouchers, and conditions.
            Pass a Vietnamese query for best results."""
            return vs.search(query, top_k=top_k)

        self.policy_tools = [search_policy]

        # Compile graph
        self.graph = self._compile_graph()

    # ------------------------------------------------------------------
    # Internal ReAct loop
    # ------------------------------------------------------------------

    def _run_agent(
        self,
        tools: list,
        system_prompt: str,
        user_message: str,
        max_iterations: int = 8,
    ) -> tuple[str, list]:
        """Run a simple ReAct tool loop; returns (final_content, messages)."""
        tool_map = {t.name: t for t in tools}
        llm_bound = self.llm.bind_tools(tools) if tools else self.llm

        messages: list = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]

        for _ in range(max_iterations):
            response = llm_bound.invoke(messages)
            messages.append(response)

            tool_calls = getattr(response, "tool_calls", None) or []
            if not tool_calls:
                break

            for tc in tool_calls:
                tool_name = tc["name"]
                if tool_name not in tool_map:
                    result_str = f"Unknown tool: {tool_name}"
                else:
                    try:
                        raw = tool_map[tool_name].invoke(tc["args"])
                        result_str = json.dumps(raw, ensure_ascii=False, default=str)
                    except Exception as exc:
                        result_str = f"Error calling {tool_name}: {exc}"

                messages.append(
                    ToolMessage(
                        content=result_str,
                        tool_call_id=tc["id"],
                        name=tool_name,
                    )
                )

        return get_last_ai_content(messages), messages

    # ------------------------------------------------------------------
    # Graph nodes (instance methods so they close over self)
    # ------------------------------------------------------------------

    def _supervisor_node(self, state: ShoppingState) -> ShoppingState:
        question = state["question"]
        prompt = SUPERVISOR_PROMPT.format(question=question)
        response = self.llm.invoke([HumanMessage(content=prompt)])
        content = str(response.content)
        route = extract_json_payload(content)
        if not route or "status" not in route:
            route = {
                "status": "ok",
                "needs_policy": True,
                "needs_data": False,
                "clarification_question": None,
            }

        return {
            "route": route,
            "trace": [{
                "step": "supervisor",
                "input": question,
                "output": route,
                "raw": content,
                "ts": timestamp_utc(),
            }],
        }

    def _worker_1_policy_node(self, state: ShoppingState) -> ShoppingState:
        question = state["question"]
        final_content, messages = self._run_agent(
            tools=self.policy_tools,
            system_prompt=POLICY_WORKER_SYSTEM,
            user_message=question,
        )

        policy_result = extract_json_payload(final_content)
        if not policy_result or "status" not in policy_result:
            policy_result = {
                "status": "ok",
                "summary": final_content,
                "facts": [],
                "citations": [],
            }

        return {
            "policy_result": policy_result,
            "trace": [{
                "step": "worker_1_policy",
                "messages": [serialize_message(m) for m in messages],
                "output": policy_result,
                "ts": timestamp_utc(),
            }],
        }

    def _worker_2_data_node(self, state: ShoppingState) -> ShoppingState:
        question = state["question"]
        final_content, messages = self._run_agent(
            tools=self.data_tools,
            system_prompt=DATA_WORKER_SYSTEM,
            user_message=question,
        )

        data_result = extract_json_payload(final_content)
        if not data_result or "status" not in data_result:
            data_result = {
                "status": "ok",
                "summary": final_content,
                "facts": [],
                "missing_fields": [],
                "not_found_entities": [],
            }

        return {
            "data_result": data_result,
            "trace": [{
                "step": "worker_2_data",
                "messages": [serialize_message(m) for m in messages],
                "output": data_result,
                "ts": timestamp_utc(),
            }],
        }

    def _worker_3_response_node(self, state: ShoppingState) -> ShoppingState:
        question = state.get("question", "")
        route = state.get("route", {})
        policy_result = state.get("policy_result", {})
        data_result = state.get("data_result", {})

        prompt = RESPONSE_WORKER_PROMPT.format(
            question=question,
            route=dump_json(route),
            policy_result=dump_json(policy_result) if policy_result else "N/A",
            data_result=dump_json(data_result) if data_result else "N/A",
        )

        response = self.llm.invoke([HumanMessage(content=prompt)])
        final_answer = str(response.content)

        return {
            "final_answer": final_answer,
            "trace": [{
                "step": "worker_3_response",
                "output": final_answer,
                "ts": timestamp_utc(),
            }],
        }

    # ------------------------------------------------------------------
    # Routing functions
    # ------------------------------------------------------------------

    def _route_after_supervisor(self, state: ShoppingState) -> str:
        route = state.get("route", {})
        if route.get("status") == "clarification_needed":
            return "worker_3_response"
        if route.get("needs_policy", False):
            return "worker_1_policy"
        if route.get("needs_data", False):
            return "worker_2_data"
        return "worker_3_response"

    def _route_after_policy(self, state: ShoppingState) -> str:
        route = state.get("route", {})
        if route.get("needs_data", False):
            return "worker_2_data"
        return "worker_3_response"

    # ------------------------------------------------------------------
    # Graph compilation
    # ------------------------------------------------------------------

    def _compile_graph(self) -> Any:
        workflow = StateGraph(ShoppingState)

        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("worker_1_policy", self._worker_1_policy_node)
        workflow.add_node("worker_2_data", self._worker_2_data_node)
        workflow.add_node("worker_3_response", self._worker_3_response_node)

        workflow.set_entry_point("supervisor")

        workflow.add_conditional_edges(
            "supervisor",
            self._route_after_supervisor,
            {
                "worker_1_policy": "worker_1_policy",
                "worker_2_data": "worker_2_data",
                "worker_3_response": "worker_3_response",
            },
        )
        workflow.add_conditional_edges(
            "worker_1_policy",
            self._route_after_policy,
            {
                "worker_2_data": "worker_2_data",
                "worker_3_response": "worker_3_response",
            },
        )
        workflow.add_edge("worker_2_data", "worker_3_response")
        workflow.add_edge("worker_3_response", END)

        return workflow.compile()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ask(
        self,
        question: str,
        trace_file: Path | None = None,
        rebuild_index: bool = False,
    ) -> dict[str, Any]:
        if rebuild_index:
            self.vector_store.rebuild(self.settings.policy_path)

        initial_state: ShoppingState = {"question": question, "trace": []}
        result = self.graph.invoke(initial_state)

        payload = {
            "question": question,
            "route": result.get("route", {}),
            "policy_result": result.get("policy_result", {}),
            "data_result": result.get("data_result", {}),
            "final_answer": result.get("final_answer", ""),
            "trace": result.get("trace", []),
        }

        if trace_file:
            p = Path(trace_file)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(dump_json(payload), encoding="utf-8")

        return payload

    def run_batch(
        self,
        test_file: Path,
        output_dir: Path,
        rebuild_index: bool = False,
    ) -> dict[str, Any]:
        test_file = Path(test_file)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        tests = json.loads(test_file.read_text(encoding="utf-8"))
        results = []
        first = True

        for test in tests:
            qid = test.get("id", f"q{len(results)}")
            question = test["question"]
            trace_path = output_dir / f"trace_{qid}.json"

            try:
                result = self.ask(
                    question=question,
                    trace_file=trace_path,
                    rebuild_index=(rebuild_index and first),
                )
                first = False
                results.append({
                    "id": qid,
                    "question": question,
                    "expected_route": test.get("expected_route", []),
                    "expected_status": test.get("expected_status", ""),
                    "actual_route": result.get("route", {}),
                    "final_answer": result.get("final_answer", ""),
                    "status": "ok",
                })
            except Exception as exc:
                first = False
                results.append({
                    "id": qid,
                    "question": question,
                    "status": "error",
                    "error": str(exc),
                })

        summary = {
            "total": len(results),
            "ok": sum(1 for r in results if r.get("status") == "ok"),
            "error": sum(1 for r in results if r.get("status") == "error"),
            "results": results,
        }

        (output_dir / "summary.json").write_text(dump_json(summary), encoding="utf-8")
        return summary


# ------------------------------------------------------------------
# Module-level helpers (kept for backward compatibility with CLI)
# ------------------------------------------------------------------

def build_graph() -> Any:
    """Build and return the compiled LangGraph workflow."""
    return ShoppingAssistant()._compile_graph()


def supervisor_node(state: ShoppingState) -> ShoppingState:
    raise NotImplementedError("Use ShoppingAssistant directly.")


def worker_1_policy_node(state: ShoppingState) -> ShoppingState:
    raise NotImplementedError("Use ShoppingAssistant directly.")


def worker_2_data_node(state: ShoppingState) -> ShoppingState:
    raise NotImplementedError("Use ShoppingAssistant directly.")


def worker_3_response_node(state: ShoppingState) -> ShoppingState:
    raise NotImplementedError("Use ShoppingAssistant directly.")
