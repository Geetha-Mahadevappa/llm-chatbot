"""Command-line interface for querying the coding assistant."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Sequence
 
from app.rag_chain import create_rag_chain
from app.types import SourceDocument
 
 
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
    parser.add_argument(
        "--no-sources",
        dest="show_sources",
        action="store_false",
        help="Hide the retrieved knowledge base chunks in the output.",
    )
    parser.set_defaults(show_sources=True)
    return parser
 
 
 def _prompt_user(prompt: str) -> Iterable[str]:
     try:
         while user_input := input(prompt):
             yield user_input
     except EOFError:
         return
 
 
def _format_source_path(raw_path: str | None) -> str:
    if not raw_path:
        return "Unknown source"

    path = Path(raw_path)
    try:
        project_root = Path(__file__).resolve().parents[1]
        return str(path.resolve().relative_to(project_root))
    except (ValueError, RuntimeError):
       return str(path)


def _print_sources(sources: Sequence[SourceDocument]) -> None:
    if not sources:
        return

    print("Sources:")
    for index, doc in enumerate(sources, start=1):
        source = _format_source_path(doc.metadata.get("source"))
        preview = doc.page_content.strip().replace("\n", " ")
        if len(preview) > 160:
            preview = f"{preview[:157]}..."
        print(f"  {index}. {source}\n     {preview}")


 def main(argv: list[str] | None = None) -> int:
     parser = _build_parser()
     args = parser.parse_args(argv)
 

    rag_chain = create_rag_chain(
        top_k=args.top_k,
        temperature=args.temperature,
        return_source_documents=args.show_sources,
    )
 
     if args.question:
         question = " ".join(args.question)
         result = rag_chain.invoke({"query": question})
        if isinstance(result, dict):
            response = result.get("result")
        else:
            response = result
        print(response)
        if args.show_sources and isinstance(result, dict):
            _print_sources(result.get("source_documents", []))
         return 0
 
     print("Interactive mode — press Ctrl+D to exit.")
     for question in _prompt_user("You> "):
         if not question.strip():
             continue
         result = rag_chain.invoke({"query": question})
        if isinstance(result, dict):
            response = result.get("result")
        else:
            response = result
         print(f"Assistant> {response}")
        if args.show_sources and isinstance(result, dict):
            _print_sources(result.get("source_documents", []))
 
     return 0
 
 
 if __name__ == "__main__":
     sys.exit(main())
