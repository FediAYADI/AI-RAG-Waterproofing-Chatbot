"""
AI RAG Waterproofing Chatbot - Command Line Interface

Usage (from the project root):
    python backend/cli.py                 # interactive chat (default)
    python backend/cli.py chat [options]  # interactive chat
    python backend/cli.py ask "question"  # single question, then exit
    python backend/cli.py ingest [PATH]   # load documents into the vector store
    python backend/cli.py stats           # show vector store statistics
"""

import argparse
import os
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import PROJECT_ROOT, settings

EXIT_COMMANDS = {"exit", "quit", ":q", "/exit", "/quit"}
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "processed"
PREVIEW_CHARS = 300

HELP_TEXT = """\
Commands:
  /help              Show this help
  /sources on|off    Show or hide retrieved sources
  /chunks on|off     Show or hide retrieved chunk text
  /rag on|off        Enable or disable retrieval (off = plain LLM answer)
  /stats             Show vector store statistics
  exit, quit         Leave the chatbot (Ctrl+C / Ctrl+D also work)
"""


def _display_path(path: str) -> str:
    try:
        return str(Path(path).resolve().relative_to(PROJECT_ROOT))
    except (ValueError, OSError):
        return path


def print_sources(sources: list, show_chunks: bool) -> None:
    if not sources:
        print("\nSources: none retrieved")
        return
    print("\nSources:")
    for i, src in enumerate(sources, 1):
        location = _display_path(src.get("source", "Unknown"))
        chunk = src.get("chunk_index")
        chunk_label = f", chunk {chunk}" if chunk is not None else ""
        print(f"  [{i}] {location}{chunk_label} (relevance: {src.get('relevance', 0):.2f})")
        if show_chunks and src.get("content"):
            preview = " ".join(src["content"].split())
            if len(preview) > PREVIEW_CHARS:
                preview = preview[:PREVIEW_CHARS] + "..."
            print(textwrap.indent(textwrap.fill(preview, width=96), "      "))


def answer_question(question: str, use_rag: bool, show_sources: bool, show_chunks: bool) -> None:
    from core.rag_engine import rag_engine

    result = rag_engine.process_query(query=question, use_rag=use_rag)
    print(f"\nAssistant: {result['answer']}")
    if use_rag and show_sources:
        print_sources(result["sources"], show_chunks)


def print_stats() -> None:
    from services.vector_service import vector_service

    stats = vector_service.get_collection_stats()
    print(f"Vector store : {settings.vector_db.path}")
    print(f"Collection   : {stats.get('collection_name', settings.vector_db.collection_name)}")
    print(f"Chunks stored: {stats.get('document_count', 0)}")


def _toggle(arg: str, current: bool) -> bool:
    if arg in ("on", "true", "1"):
        return True
    if arg in ("off", "false", "0"):
        return False
    return not current


def _missing_api_keys() -> list:
    required = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    keys = {required.get(settings.llm.provider), required.get(settings.embedding.provider)}
    return sorted(k for k in keys if k and not os.getenv(k))


def run_chat(args: argparse.Namespace) -> int:
    try:
        import readline  # noqa: F401  (enables arrow-key history where available)
    except ImportError:
        pass

    print("=" * 60)
    print(f"{settings.app.name} - CLI")
    print("=" * 60)
    print("Loading RAG pipeline...")
    from core.rag_engine import rag_engine  # noqa: F401  (initializes services)
    from services.vector_service import vector_service

    count = vector_service.get_collection_stats().get("document_count", 0)
    if count == 0:
        print("\nWarning: the vector store is empty. Run `python backend/cli.py ingest` first.")
    for key in _missing_api_keys():
        print(f"\nWarning: {key} is not set in config/.env; questions will fail until it is.")
    print(f"\nLLM: {settings.llm.provider}/{settings.llm.model} | "
          f"Embeddings: {settings.embedding.provider}/{settings.embedding.model} | "
          f"Chunks: {count}")
    print("Type your question, /help for commands, or 'exit' to quit.\n")

    use_rag = not args.no_rag
    show_sources = not args.no_sources
    show_chunks = args.show_chunks

    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            return 0

        if not question:
            continue
        if question.lower() in EXIT_COMMANDS:
            print("Goodbye!")
            return 0

        if question.startswith("/"):
            cmd, _, arg = question[1:].partition(" ")
            cmd, arg = cmd.lower(), arg.strip().lower()
            if cmd == "help":
                print(HELP_TEXT)
            elif cmd == "sources":
                show_sources = _toggle(arg, show_sources)
                print(f"Sources {'shown' if show_sources else 'hidden'}.")
            elif cmd == "chunks":
                show_chunks = _toggle(arg, show_chunks)
                print(f"Chunk text {'shown' if show_chunks else 'hidden'}.")
            elif cmd == "rag":
                use_rag = _toggle(arg, use_rag)
                print(f"Retrieval {'enabled' if use_rag else 'disabled'}.")
            elif cmd == "stats":
                print_stats()
            else:
                print(f"Unknown command: /{cmd}. Type /help for the list of commands.")
            continue

        try:
            answer_question(question, use_rag, show_sources, show_chunks)
        except KeyboardInterrupt:
            print("\n(Interrupted)")
        except Exception as e:
            print(f"\nError: {e}")
        print()


def run_ask(args: argparse.Namespace) -> int:
    try:
        answer_question(args.question, not args.no_rag, not args.no_sources, args.show_chunks)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def run_ingest(args: argparse.Namespace) -> int:
    from core.rag_engine import rag_engine
    from services.vector_service import vector_service

    target = Path(args.path).resolve()
    if not target.exists():
        print(f"Error: path not found: {target}", file=sys.stderr)
        return 1

    before = vector_service.get_collection_stats().get("document_count", 0)
    print(f"Ingesting: {target}")
    print(f"Current chunk count: {before}")
    if not args.yes:
        try:
            if input("Proceed? (y/n): ").strip().lower() != "y":
                print("Aborted.")
                return 0
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            return 0

    metadata = {"source": _display_path(str(target))}
    if target.is_dir():
        result = rag_engine.ingest_directory(str(target), metadata=metadata)
        print(f"\nFiles found: {result['total_files']}")
        print(f"Succeeded  : {result['successful']}")
        print(f"Failed     : {result['failed']}")
        for error in result["errors"]:
            print(f"  - {_display_path(error['file'])}: {error['error']}")
        failed = result["failed"]
    else:
        result = rag_engine.ingest_document(str(target), metadata=metadata)
        print(f"\n{result['message']}")
        failed = 0 if result["success"] else 1

    after = vector_service.get_collection_stats().get("document_count", 0)
    print(f"\nChunks added: {after - before} (total: {after})")
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python backend/cli.py",
        description="Terminal interface for the AI RAG Waterproofing Chatbot.",
    )
    sub = parser.add_subparsers(dest="command")

    def add_answer_options(p: argparse.ArgumentParser) -> None:
        p.add_argument("--no-sources", action="store_true", help="hide retrieved sources")
        p.add_argument("--show-chunks", action="store_true", help="print retrieved chunk text")
        p.add_argument("--no-rag", action="store_true", help="answer with the LLM only, no retrieval")

    chat = sub.add_parser("chat", help="start an interactive chat session (default)")
    add_answer_options(chat)
    chat.set_defaults(func=run_chat)

    ask = sub.add_parser("ask", help="answer a single question and exit")
    ask.add_argument("question")
    add_answer_options(ask)
    ask.set_defaults(func=run_ask)

    ingest = sub.add_parser("ingest", help="load documents into the vector store")
    ingest.add_argument("path", nargs="?", default=str(DEFAULT_DATA_DIR),
                        help="file or directory to ingest (default: data/processed)")
    ingest.add_argument("-y", "--yes", action="store_true", help="skip the confirmation prompt")
    ingest.set_defaults(func=run_ingest)

    stats = sub.add_parser("stats", help="show vector store statistics")
    stats.set_defaults(func=lambda _args: print_stats() or 0)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        args = parser.parse_args(["chat"] + (argv or []))
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return 130
    except Exception as e:
        # Surface setup problems (bad config, unreachable vector store, ...)
        # without a traceback.
        print(f"\nFailed to start the RAG pipeline: {e}", file=sys.stderr)
        print("Check config/config.yaml and the API keys in config/.env.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
