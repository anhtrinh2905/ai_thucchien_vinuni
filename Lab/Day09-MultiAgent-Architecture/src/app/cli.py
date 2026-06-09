from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.graph import ShoppingAssistant


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Shopping Assistant CLI.")
    parser.add_argument("--question", help="Run one question through the graph.")
    parser.add_argument("--test-file", default="data/test.json")
    parser.add_argument("--trace-file", default=None, help="Save trace JSON to this path.")
    parser.add_argument("--batch", action="store_true", help="Run batch test from --test-file.")
    parser.add_argument("--output-dir", default="src/artifacts/batch", help="Output dir for batch results.")
    parser.add_argument("--rebuild-index", action="store_true", help="Force rebuild Chroma index.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    assistant = ShoppingAssistant()

    if args.batch:
        summary = assistant.run_batch(
            test_file=Path(args.test_file),
            output_dir=Path(args.output_dir),
            rebuild_index=args.rebuild_index,
        )
        print(f"\nBatch complete: {summary['ok']}/{summary['total']} ok, {summary['error']} errors")
        print(f"Traces saved to: {args.output_dir}/")
        print(f"Summary saved to: {args.output_dir}/summary.json")

    elif args.question:
        result = assistant.ask(
            question=args.question,
            trace_file=Path(args.trace_file) if args.trace_file else None,
            rebuild_index=args.rebuild_index,
        )
        import json
        print("\n=== ROUTE ===")
        print(json.dumps(result["route"], ensure_ascii=False, indent=2))
        print("\n=== FINAL ANSWER ===")
        print(result["final_answer"])
        if args.trace_file:
            print(f"\nTrace saved to: {args.trace_file}")

    else:
        print("Usage:")
        print("  Single question: python -m app.cli --question '...'")
        print("  Batch test:      python -m app.cli --batch --test-file data/test.json")
        sys.exit(1)


if __name__ == "__main__":
    main()
