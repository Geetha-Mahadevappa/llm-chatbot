from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from vectorstore import load_vectorstore

def create_rag_chain():
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )
    return qa_chain


if __name__ == "__main__":
    create_rag_chain()