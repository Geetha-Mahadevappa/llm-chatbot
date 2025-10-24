import streamlit as st
from app.rag_chain import create_rag_chain

st.set_page_config(page_title="Code Assistant", page_icon="💻")

st.title("AI Coding Assistant (RAG + GPT-4)")
st.markdown("Ask coding questions, debug code, or generate new snippets!")

# Keep chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

rag_chain = create_rag_chain()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Ask me about Python, debugging, or code generation..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = rag_chain.run(prompt)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
