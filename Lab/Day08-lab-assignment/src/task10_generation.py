"""
Task 10 — Generation Có Citation (OpenAI gpt-4o-mini) + Agentic tool calling.

Agent chỉ gọi tool `search_context` khi câu hỏi liên quan tới dataset hiện tại
(pháp luật/chất cấm/ma tuý và tin tức nghệ sĩ liên quan). Nếu câu hỏi ngoài
phạm vi, agent KHÔNG gọi tool và trả lời rằng đây không phải lĩnh vực hỗ trợ.
"""

import json
import os

from dotenv import load_dotenv

load_dotenv()

from src.rag_utils import LLM_MODEL, get_openai_client
from src.task9_retrieval_pipeline import retrieve

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3
MAX_TOOL_TURNS = 3

OUT_OF_DOMAIN_MSG = (
    "Tôi không phải chatbot trong lĩnh vực này. "
    "Tôi chỉ hỗ trợ các câu hỏi về pháp luật/chất cấm/ma tuý "
    "và tin tức nghệ sĩ liên quan."
)

SYSTEM_PROMPT = """Bạn là trợ lý trả lời câu hỏi tiếng Việt, giới hạn trong DATASET sau:
- Văn bản pháp luật Việt Nam về ma tuý và các chất cấm.
- Bài báo về nghệ sĩ/người nổi tiếng Việt Nam liên quan tới ma tuý.

# Công cụ (tool):
Bạn có một tool tên `search_context` để tìm ngữ cảnh trong dataset trên.
- KHÔNG DÙNG TOOL nếu hỏi câu hỏi ngoài lĩnh vực và trả lời CHÍNH XÁC câu sau:
"{out_of_domain}"

# Quy tắc trả lời (sau khi đã có context từ tool):
- Mỗi nhận định/sự kiện PHẢI có citation trong ngoặc, ví dụ
  [Luật Phòng chống ma tuý 2021, Điều 3] hoặc [VTC News, 2026].
- Nếu context không đủ để trả lời, nói rõ:
  "Tôi không thể xác minh thông tin này từ nguồn hiện có".
- Trình bày rõ ràng theo đoạn.
""".replace("{out_of_domain}", OUT_OF_DOMAIN_MSG)


SEARCH_CONTEXT_TOOL = {
    "type": "function",
    "function": {
        "name": "search_context",
        "description": (
            "Tìm kiếm ngữ cảnh liên quan trong dataset gồm văn bản pháp luật về "
            "ma tuý/chất cấm và bài báo về nghệ sĩ liên quan tới ma tuý. "
            "CHỈ gọi khi câu hỏi thuộc các chủ đề này. KHÔNG gọi cho câu hỏi "
            "ngoài lĩnh vực."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Truy vấn tìm kiếm, nên cụ thể và bằng tiếng Việt.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Số đoạn ngữ cảnh cần lấy (mặc định 5).",
                },
            },
            "required": ["query"],
        },
    },
}


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp chunks để tránh lost in the middle.
    Input [1,2,3,4,5] → Output [1,3,5,4,2]
    """
    if len(chunks) <= 2:
        return chunks

    reordered = []
    for i in range(0, len(chunks), 2):
        reordered.append(chunks[i])

    start = len(chunks) - 1 if len(chunks) % 2 == 0 else len(chunks) - 2
    for i in range(start, 0, -2):
        reordered.append(chunks[i])

    return reordered


def format_context(chunks: list[dict]) -> str:
    """Format chunks với source labels cho citation."""
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        metadata = chunk.get("metadata", {})
        source = metadata.get("source", f"Source {i}")
        doc_type = metadata.get("type", "unknown")
        parts.append(
            f"[Document {i} | Source: {source} | Type: {doc_type}]\n"
            f"{chunk['content']}\n"
        )
    return "\n---\n".join(parts)


def search_context(query: str, top_k: int = TOP_K) -> dict:
    """
    Tool thực thi retrieval trên dataset.

    Returns:
        {'context': str, 'chunks': list[dict]} — context đã format + raw chunks.
    """
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {"context": "", "chunks": []}

    reordered = reorder_for_llm(chunks)
    return {"context": format_context(reordered), "chunks": reordered}


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """
    Agentic generation: LLM tự quyết định gọi tool `search_context` hay không.

    - Nếu câu hỏi thuộc dataset → LLM gọi tool, nhận context, trả lời có citation.
    - Nếu ngoài lĩnh vực → LLM không gọi tool, trả lời từ chối.
    """
    client = get_openai_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    collected_chunks: list[dict] = []
    used_search_tool = False

    for _ in range(MAX_TOOL_TURNS):
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=[SEARCH_CONTEXT_TOOL],
            tool_choice="auto",
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        message = response.choices[0].message
        tool_calls = message.tool_calls or []

        if not tool_calls:
            return {
                "answer": message.content or "",
                "sources": collected_chunks,
                "retrieval_source": (
                    collected_chunks[0].get("source", "hybrid")
                    if collected_chunks
                    else "none"
                ),
                "used_search_tool": used_search_tool,
            }

        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            }
        )

        for tool_call in tool_calls:
            if tool_call.function.name != "search_context":
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": "Unknown tool.",
                    }
                )
                continue

            used_search_tool = True
            try:
                args = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            search_query = args.get("query", query)
            search_top_k = int(args.get("top_k", top_k) or top_k)
            result = search_context(search_query, top_k=search_top_k)
            collected_chunks = result["chunks"] or collected_chunks

            tool_payload = result["context"] or (
                "Không tìm thấy ngữ cảnh phù hợp trong dataset."
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_payload,
                }
            )

    final = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        top_p=TOP_P,
    )

    return {
        "answer": final.choices[0].message.content or "",
        "sources": collected_chunks,
        "retrieval_source": (
            collected_chunks[0].get("source", "hybrid")
            if collected_chunks
            else "none"
        ),
        "used_search_tool": used_search_tool,
    }


if __name__ == "__main__":
    test_queries = [
        "Hình phạt cho tội tàng trữ trái phép chất ma tuý theo pháp luật Việt Nam?",
        "Những nghệ sĩ nào đã bị bắt vì liên quan tới ma tuý?",
        "Hôm nay thời tiết Hà Nội thế nào?",
    ]

    for q in test_queries:
        print(f"\n{'=' * 70}")
        print(f"Q: {q}")
        print("=" * 70)
        result = generate_with_citation(q)
        print(f"\nA: {result['answer']}")
        print(
            f"\n[Sources: {len(result['sources'])} chunks | "
            f"via {result['retrieval_source']} | "
            f"used_tool={result['used_search_tool']}]"
        )
