"""Utilities for creating and loading the FAISS vector store."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "knowledge_base"
DEFAULT_INDEX_PATH = PROJECT_ROOT / "faiss_index"


load_dotenv(PROJECT_ROOT / ".env")


def _load_documents(data_path: Path) -> Sequence:
    """Load markdown and text files from ``data_path`` into LangChain documents."""

    docs = []
    for pattern in ("**/*.txt", "**/*.md"):
        loader = DirectoryLoader(
            str(data_path),
            glob=pattern,
            show_progress=True,
        )
        docs.extend(loader.load())
    return docs


def create_vectorstore(
    data_path: str | Path = DEFAULT_DATA_PATH,
    index_path: str | Path = DEFAULT_INDEX_PATH,
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
):
    """Build the FAISS vector store from the knowledge base documents."""

    data_path = Path(data_path)
    index_path = Path(index_path)
    documents = _load_documents(data_path)
    if not documents:
        raise FileNotFoundError(
            f"No knowledge base documents found in '{data_path}'. "
            "Add .txt or .md files before creating the vector store."
        )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(str(index_path))
    print(f"Vectorstore created and saved to '{index_path}'.")


def load_vectorstore(index_path: str | Path = DEFAULT_INDEX_PATH):
    """Load the FAISS vector store if it has been created previously."""

    index_path = Path(index_path)
    if not index_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found at '{index_path}'. Run create_vectorstore() first."
        )

    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(
        str(index_path), embeddings, allow_dangerous_deserialization=True
    )


if __name__ == "__main__":
    create_vectorstore()
