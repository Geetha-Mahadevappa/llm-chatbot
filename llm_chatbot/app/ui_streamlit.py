"""Streamlit UI for the RAG-based coding assistant."""

from __future__ import annotations

import streamlit as st

from app.rag_chain import create_rag_chain


st.set_page_config(page_title="Code Assistant", page_icon="💻")


def _initialize_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "retrieval_settings" not in st.session_state:
        st.session_state.retrieval_settings = {"top_k": 3, "temperature": 0.3}

    if "rag_chain" not in st.session_state:
        settings = st.session_state.retrieval_settings
        st.session_state.rag_chain = create_rag_chain(
            top_k=settings["top_k"], temperature=settings["temperature"]
        )


def _render_sidebar() -> None:
    st.sidebar.header("Assistant settings")
    st.sidebar.caption(
        "Tune how many documents are retrieved and how creative the model should be."
    )

    current_settings = st.session_state.retrieval_settings
    top_k = st.sidebar.slider(
        "Retrieved chunks",
        min_value=1,
        max_value=8,
        value=current_settings["top_k"],
        help="Higher values provide more context at the cost of speed.",
    )
    temperature = st.sidebar.slider(
        "Response creativity",
        min_value=0.0,
        max_value=1.0,
        value=float(current_settings["temperature"]),
        step=0.1,
        help="Lower values yield deterministic answers; higher values allow more exploration.",
    )

    if (top_k, temperature) != (
        current_settings["top_k"],
        current_settings["temperature"],
    ):
        st.session_state.retrieval_settings = {"top_k": top_k, "temperature": temperature}
        st.session_state.rag_chain = create_rag_chain(top_k=top_k, temperature=temperature)

    if st.sidebar.button("Clear conversation"):
        st.session_state.messages = []
        st.experimental_rerun()

    st.sidebar.divider()
    st.sidebar.markdown(
        "Need to update the knowledge base? Run `python -m app.vectorstore` after adding files."
    )


def _display_chat_history() -> None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def main() -> None:
    st.title("AI Coding Assistant (RAG + GPT-4)")
    st.markdown("Ask coding questions, debug code, or generate new snippets!")

    _initialize_session_state()
    _render_sidebar()
    _display_chat_history()

    if prompt := st.chat_input(
        "Ask me about Python, debugging, or code generation..."
    ):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.rag_chain.invoke({"query": prompt})
                response = result.get("result") if isinstance(result, dict) else str(result)
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
