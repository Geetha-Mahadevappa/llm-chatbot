"""Command-line interface for querying the coding assistant."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable

from app.rag_chain import create_rag_chain


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="*", help="Question to ask the assistant")
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of knowledge base chunks to retrieve.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Sampling temperature for the LLM (0 for deterministic responses).",
    )
    return parser


def _prompt_user(prompt: str) -> Iterable[str]:
    try:
        while user_input := input(prompt):
            yield user_input
    except EOFError:
        return


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    rag_chain = create_rag_chain(top_k=args.top_k, temperature=args.temperature)

    if args.question:
        question = " ".join(args.question)
        result = rag_chain.invoke({"query": question})
        print(result.get("result") if isinstance(result, dict) else result)
        return 0

    print("Interactive mode — press Ctrl+D to exit.")
    for question in _prompt_user("You> "):
        if not question.strip():
            continue
        result = rag_chain.invoke({"query": question})
        response = result.get("result") if isinstance(result, dict) else result
        print(f"Assistant> {response}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
