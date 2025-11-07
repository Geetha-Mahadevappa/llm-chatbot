"""Streamlit UI for the RAG-based coding assistant."""
 
 from __future__ import annotations
 
 from pathlib import Path
 from typing import Sequence
 import streamlit as st
 
 from app.rag_chain import create_rag_chain
 from app.types import SourceDocument


PROJECT_ROOT = Path(__file__).resolve().parents[1]
 
 
 st.set_page_config(page_title="Code Assistant", page_icon="💻")
 
 
 def _initialize_session_state() -> None:
     if "messages" not in st.session_state:
         st.session_state.messages = []
 
     if "retrieval_settings" not in st.session_state:
         st.session_state.retrieval_settings = {"top_k": 3, "temperature": 0.3}
 
     if "show_sources" not in st.session_state:
        st.session_state.show_sources = True

     if "rag_chain" not in st.session_state:
         settings = st.session_state.retrieval_settings
         st.session_state.rag_chain = create_rag_chain(
            top_k=settings["top_k"],
            temperature=settings["temperature"],
            return_source_documents=st.session_state.show_sources,
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
 
    show_sources = st.sidebar.checkbox(
        "Show source documents",
        value=st.session_state.show_sources,
        help="Display which knowledge base chunks were retrieved for each answer.",
    )

     if (top_k, temperature) != (
         current_settings["top_k"],
         current_settings["temperature"],
     ):
        st.session_state.retrieval_settings = {"top_k": top_k, "temperature": temperature}
        st.session_state.rag_chain = create_rag_chain(
            top_k=top_k,
            temperature=temperature,
            return_source_documents=show_sources,
        )

    if show_sources != st.session_state.show_sources:
        st.session_state.show_sources = show_sources
        st.session_state.rag_chain = create_rag_chain(
            top_k=top_k,
            temperature=temperature,
            return_source_documents=show_sources,
        )
 
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
 
 
def _render_sources(sources: Sequence[SourceDocument]) -> None:
    if not sources:
        return

    with st.expander("Sources", expanded=False):
        for doc in sources:
            source = doc.metadata.get("source")
            if source:
                path = Path(source)
                try:
                    source = str(path.resolve().relative_to(PROJECT_ROOT))
                except (ValueError, RuntimeError):
                    source = str(path)
            else:
                source = "Unknown source"

            preview = doc.page_content.strip().replace("\n", " ")
            if len(preview) > 220:
                preview = f"{preview[:217]}..."

            st.markdown(f"**{source}**\n\n{preview}")


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
 
                if (
                    st.session_state.show_sources
                    and isinstance(result, dict)
                    and result.get("source_documents")
                ):
                    _render_sources(result["source_documents"])

         st.session_state.messages.append({"role": "assistant", "content": response})
 
 
 if __name__ == "__main__":
     main()
