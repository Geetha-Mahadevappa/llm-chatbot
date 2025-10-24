import langchain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

def create_vectorstore(data_path="data/knowledge_base"):
    loader = DirectoryLoader(data_path, glob="**/*.txt", show_progress=True)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local("faiss_index")
    print("Vectorstore created and saved locally.")

def load_vectorstore():
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)


if __name__ == "__main__":
    create_vectorstore()
