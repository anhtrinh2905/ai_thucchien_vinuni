"""
Day 1 — LLM API Foundation
AICB-P1: AI Practical Competency Program, Phase 1

Instructions:
    1. Fill in every section marked with TODO.
    2. Do NOT change function signatures.
    3. Copy this file to solution/solution.py when done.
    4. Run: pytest tests/ -v
"""

import os
import time
from dotenv import load_dotenv
from typing import Any, Callable
import openai


# Initialize OpenAI client using API key from environment variable
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


# ---------------------------------------------------------------------------
# Estimated costs per 1K OUTPUT tokens (USD) — update if pricing changes
# ---------------------------------------------------------------------------
COST_PER_1K_OUTPUT_TOKENS = {
    "gpt-4o": 0.010,
    "gpt-4o-mini": 0.0006,
}

OPENAI_MODEL = "gpt-4o"
OPENAI_MINI_MODEL = "gpt-4o-mini"


# ---------------------------------------------------------------------------
# Task 1 — Call GPT-4o
# ---------------------------------------------------------------------------
def call_openai(
    prompt: str,
    model: str = OPENAI_MODEL,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 256,
) -> tuple[str, float]:
    """
    Call the OpenAI Chat Completions API and return the response text + latency.

    Args:
        prompt:      The user message to send.
        model:       The OpenAI model to use (default: gpt-4o).
        temperature: Sampling temperature (0.0 – 2.0).
        top_p:       Nucleus sampling threshold.
        max_tokens:  Maximum number of tokens to generate.

    Returns:
        A tuple of (response_text: str, latency_seconds: float).

    Hint:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    """
    # TODO: import OpenAI, create client, call chat.completions.create,
    #       measure start/end time, return (response_text, latency)
    client = openai.OpenAI(api_key=api_key or "sk-test")
    start_time = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
    )
    end_time = time.time()
    response_text = response.choices[0].message.content
    latency_seconds = end_time - start_time
    return response_text, latency_seconds


# ---------------------------------------------------------------------------
# Task 2 — Call GPT-4o-mini
# ---------------------------------------------------------------------------
def call_openai_mini(
    prompt: str,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 256,
) -> tuple[str, float]:
    """
    Call the OpenAI Chat Completions API using gpt-4o-mini and return the
    response text + latency.

    Args:
        prompt:      The user message to send.
        temperature: Sampling temperature (0.0 – 2.0).
        top_p:       Nucleus sampling threshold.
        max_tokens:  Maximum number of tokens to generate.

    Returns:
        A tuple of (response_text: str, latency_seconds: float).

    Hint:
        Reuse call_openai() by passing model=OPENAI_MINI_MODEL.
    """
    # TODO: call call_openai with model=OPENAI_MINI_MODEL
    response_text, latency_seconds = call_openai(
        prompt=prompt,
        model=OPENAI_MINI_MODEL,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
    )
    return response_text, latency_seconds


# ---------------------------------------------------------------------------
# Task 3 — Compare GPT-4o vs GPT-4o-mini
# ---------------------------------------------------------------------------
def compare_models(prompt: str) -> dict:
    """
    Call both gpt-4o and gpt-4o-mini with the same prompt and return a
    comparison dictionary.

    Args:
        prompt: The user message to send to both models.

    Returns:
        A dict with keys:
            - "gpt4o_response":      str
            - "mini_response":       str
            - "gpt4o_latency":       float
            - "mini_latency":        float
            - "gpt4o_cost_estimate": float  (estimated USD for the response)

    Hint:
        Cost estimate = (len(response.split()) / 0.75) / 1000 * COST_PER_1K_OUTPUT_TOKENS["gpt-4o"]
        (0.75 words ≈ 1 token is a rough approximation)
    """
    # TODO: call call_openai and call_openai_mini, assemble and return the dict

    gpt4o_response, gpt4o_latency = call_openai(prompt=prompt, model=OPENAI_MODEL)
    mini_response, mini_latency = call_openai_mini(prompt=prompt)

    gpt4o_cost_estimate = (len(gpt4o_response.split()) / 0.75) / 1000 * COST_PER_1K_OUTPUT_TOKENS[OPENAI_MODEL]

    return {
        "gpt4o_response": gpt4o_response,
        "mini_response": mini_response,
        "gpt4o_latency": gpt4o_latency,
        "mini_latency": mini_latency,
        "gpt4o_cost_estimate": gpt4o_cost_estimate,
    }


# ---------------------------------------------------------------------------
# Task 4 — Streaming chatbot with conversation history
# ---------------------------------------------------------------------------
def streaming_chatbot() -> None:
    """
    Run an interactive streaming chatbot in the terminal.

    Behaviour:
        - Streams tokens from OpenAI as they arrive (print each chunk).
        - Maintains the last 3 conversation turns in history.
        - Typing 'quit' or 'exit' ends the loop.

    Hints:
        - Keep a list `history` of {"role": ..., "content": ...} dicts.
        - Use stream=True in client.chat.completions.create() and iterate:
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                print(delta, end="", flush=True)
        - After each turn, append the assistant reply to history.
        - Trim history to the last 3 turns: history = history[-3:]
    """
    # TODO: enter while-loop, read user input, stream response, maintain history
    client = openai.OpenAI(api_key=api_key or "sk-test")
    history = []
    
    print("Chatbot started. Type 'quit' or 'exit' to end.")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Add user message to history
        history.append({"role": "user", "content": user_input})
        
        # Stream response from OpenAI
        print("Assistant: ", end="", flush=True)
        assistant_response = ""
        
        stream = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=history,
            stream=True,
            max_tokens=1024
        )
        
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            assistant_response += delta
        
        print()  # Newline after response
        
        # Add assistant reply to history
        history.append({"role": "assistant", "content": assistant_response})
        
        # Keep only last 3 turns (within reasonable limits)
        if len(history) > 6:  # 3 turns = 6 messages (3 user + 3 assistant)
            history = history[-6:]


# ---------------------------------------------------------------------------
# Bonus Task A — Retry with exponential backoff
# ---------------------------------------------------------------------------
def retry_with_backoff(
    fn: Callable,
    max_retries: int = 3,
    base_delay: float = 0.1,
) -> Any:
    """
    Call fn(). If it raises an exception, retry up to max_retries times
    with exponential backoff (base_delay * 2^attempt).

    Args:
        fn:          Zero-argument callable to execute.
        max_retries: Maximum number of retry attempts.
        base_delay:  Initial delay in seconds before the first retry.

    Returns:
        The return value of fn() on success.

    Raises:
        The last exception raised by fn() after all retries are exhausted.
    """
    # TODO: implement retry loop with exponential backoff
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
    
    # If we exhausted all retries, raise the last exception
    if last_exception:
        raise last_exception


# ---------------------------------------------------------------------------
# Bonus Task B — Batch compare
# ---------------------------------------------------------------------------
def batch_compare(prompts: list[str]) -> list[dict]:
    """
    Run compare_models on each prompt in the list.

    Args:
        prompts: List of prompt strings.

    Returns:
        List of dicts, each being the compare_models result with an extra
        key "prompt" containing the original prompt string.
    """
    # TODO: iterate over prompts, call compare_models, add "prompt" key
    results = []
    for prompt in prompts:
        result = compare_models(prompt)
        result["prompt"] = prompt
        results.append(result)
    return results


# ---------------------------------------------------------------------------
# Bonus Task C — Format comparison table
# ---------------------------------------------------------------------------
def format_comparison_table(results: list[dict]) -> str:
    """
    Format a list of compare_models results as a readable text table.

    Args:
        results: List of dicts as returned by batch_compare.

    Returns:
        A formatted string table with columns:
        Prompt | GPT-4o Response | Mini Response | GPT-4o Latency | Mini Latency

    Hint:
        Truncate long text to 40 characters for readability.
    """
    # TODO: build and return a formatted table string
    def truncate(text, length=40):
        if len(text) > length:
            return text[:length-3] + "..."
        return text
    
    # Build header
    headers = ["Prompt", "GPT-4o Response", "Mini Response", "GPT-4o Latency", "Mini Latency"]
    col_width = 40
    
    header_line = " | ".join(f"{h:<{col_width}}" for h in headers)
    separator = "-" * (len(header_line))
    
    lines = [header_line, separator]
    
    # Add rows
    for result in results:
        prompt = truncate(result.get("prompt", ""), col_width)
        gpt4o_resp = truncate(result.get("gpt4o_response", ""), col_width)
        mini_resp = truncate(result.get("mini_response", ""), col_width)
        gpt4o_latency = f"{result.get('gpt4o_latency', 0):.3f}s"
        mini_latency = f"{result.get('mini_latency', 0):.3f}s"
        
        row = " | ".join([
            f"{prompt:<{col_width}}",
            f"{gpt4o_resp:<{col_width}}",
            f"{mini_resp:<{col_width}}",
            f"{gpt4o_latency:<{col_width}}",
            f"{mini_latency:<{col_width}}"
        ])
        lines.append(row)
    
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point for manual testing
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_prompt = "Explain the difference between temperature and top_p in one sentence."
    print("=== Comparing models ===")
    result = compare_models(test_prompt)
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n=== Starting chatbot (type 'quit' to exit) ===")
    streaming_chatbot()
