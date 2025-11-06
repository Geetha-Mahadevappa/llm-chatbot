"""Utilities for composing the Retrieval-Augmented Generation chain."""

from typing import Optional

from langchain.chains import RetrievalQA
from langchain.schema import BaseRetriever
from langchain_openai import ChatOpenAI

from .vectorstore import load_vectorstore


def create_rag_chain(
    *,
    top_k: int = 3,
    temperature: float = 0.3,
    model: str = "gpt-4o-mini",
    retriever: Optional[BaseRetriever] = None,
):
    """Create a RetrievalQA chain configured for the coding assistant.

    Args:
        top_k: Number of documents to retrieve from the vector store.
        temperature: Sampling temperature used by the LLM.
        model: Chat model identifier.
        retriever: Optional pre-configured retriever. When ``None`` the
            default FAISS retriever is loaded from disk.

    Returns:
        A ``RetrievalQA`` chain ready to execute queries.
    """

    if retriever is None:
        vectorstore = load_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    elif hasattr(retriever, "search_kwargs"):
        retriever.search_kwargs["k"] = top_k

    llm = ChatOpenAI(model=model, temperature=temperature)

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
    )


if __name__ == "__main__":
    create_rag_chain()