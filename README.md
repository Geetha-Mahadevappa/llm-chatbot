 # 💻 AI Coding Assistant (RAG + LangChain + OpenAI)
 
 ## 📘 Overview
 
 This project is an **AI-powered coding assistant** built using **LangChain**, **OpenAI GPT**, and **FAISS**.
 It uses **Retrieval-Augmented Generation (RAG)** to answer programming and debugging-related questions.
 
 Instead of relying solely on the model’s internal knowledge, it retrieves relevant information from a **local knowledge base** — containing documents like `debugging_guide.md` and `python_tips.txt` — and combines it with GPT reasoning to produce accurate, context-aware answers.
 
 ---
 
 ## 🧠 Features
 
 * 🧩 **Retrieval-Augmented Generation (RAG)** pipeline using LangChain
 * 🧠 **Custom Knowledge Base**: stored locally in `data/knowledge_base/`
 * 💬 **ChatGPT-style Interface** built with Streamlit
+* 📚 **Transparent Retrieval** — review the exact knowledge base snippets that informed each answer
 * ⚙️ **OpenAI API Integration** for high-quality responses
 * 🔒 Secure configuration via `.env` file (API keys are never exposed)
 
 ---
 
 ## 🧩 Project Structure
 
 ```
 rag_coding_assistant/
 │
 ├── app/
 │   ├── ui_streamlit.py      # Streamlit-based chat UI
 │   ├── rag_chain.py         # Defines the RAG pipeline (Retriever + LLM)
 │   ├── vectorstore.py       # Builds and loads FAISS vector database
 │
 ├── data/
 │   └── knowledge_base/
 │       ├── debugging_guide.md   # Troubleshooting & debugging tips
 │       ├── python_tips.txt      # Python tricks and common pitfalls
 │
 ├── .env                    # Stores API keys (not uploaded to GitHub)
 ├── requirements.txt
 └── README.md
 ```
 
@@ -106,60 +107,62 @@ You can **add more `.txt` or `.md` files** here to expand your assistant’s kno
 * Splits documents into smaller chunks for embedding
 * Uses `OpenAIEmbeddings()` to create vector representations
 * Stores embeddings locally in a **FAISS** index
 * Run this once to build the vectorstore:
 
   ```bash
   python -m app.vectorstore
   ```
 
 ---
 
 ### `app/rag_chain.py`
 
 * Loads the FAISS vectorstore and wraps it in a retriever
 * Initializes the OpenAI LLM (`gpt-4o-mini`)
 * Combines retrieval and generation via `RetrievalQA`
 * Acts as the **core logic** for the chatbot’s reasoning
 
 ---
 
 ### `app/ui_streamlit.py`
 
 * Provides an **interactive web UI** (similar to ChatGPT)
 * Maintains chat history using Streamlit session state
 * Sends user queries to the RAG chain and displays answers
+* Lets you toggle and inspect the retrieved source documents for every reply
 * Run this to start the chatbot:
 
   ```bash
   streamlit run app/ui_streamlit.py
   ```
 
 ### `app/cli.py`
 
 * Lightweight command-line interface for quick questions
 * Supports adjusting retrieval depth and model temperature
+* Displays the retrieved sources alongside answers (disable with `--no-sources`)
 * Ask a single question:
 
   ```bash
   python -m app.cli "How do I reverse a string in Python?"
   ```
 
 * Start an interactive prompt:
 
   ```bash
   python -m app.cli
   ```
 
 ---
 
 ## 🧩 How It Works
 
 1. You type a coding or debugging question in the chat.
 2. The app retrieves relevant text chunks from your `knowledge_base` using FAISS.
 3. The retrieved context is passed to the OpenAI GPT model.
 4. The model generates an accurate, context-aware response.

```
User Question
     ↓
Vectorstore Retriever (FAISS)
     ↓
LangChain RAG (Retriever + LLM)
     ↓
OpenAI GPT Response
     ↓
Streamlit Chat UI
```

---

## 🧪 Example Queries

You can try:

```
> How do I fix a syntax error in Python?
> What are some debugging best practices?
> Show me how to create a Python function that reverses a string.
> How do I handle exceptions in Python?
```

---

## 🔒 Environment Variables

| Variable               | Description                                  |
| ---------------------- | -------------------------------------------- |
| `OPENAI_API_KEY`       | Your OpenAI API key                          |
| `LANGCHAIN_API_KEY`    | API key for LangSmith (optional for tracing) |
| `LANGCHAIN_TRACING_V2` | Enable tracing of LangChain runs             |
| `LANGCHAIN_PROJECT`    | Project name for LangSmith dashboard         |

---

Would you like me to generate a **short GitHub “About” description (1–2 lines)** for your repo page — the one that appears at the top under your project tit
