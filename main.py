from fastapi import FastAPI
import os
from pydantic import BaseModel
from langchain_ollama.llms import OllamaLLM
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


os.environ["USER_AGENT"] = "ChatbotAPI/1.0"
os.environ["BASE_URL"] = 'http://51.8.45.150:11434'


rag_chain = None



@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_chain

    pdf_loader = PyPDFLoader("./AI_Engineer.pdf")
    pages = [page async for page in pdf_loader.alazy_load()]

    web_loader = WebBaseLoader(
        web_paths=("https://www.promtior.ai/service/", "https://www.promtior.ai")
    )
    web_docs = web_loader.load()
    docs = pages + web_docs

  
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_model)
    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    llm = OllamaLLM(model='llama3.2', base_url=os.getenv("BASE_URL",'http://51.8.45.150:11434'))
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class QuestionRequest(BaseModel):
    question: str

@app.post("/answer")
async def answer_question(request: QuestionRequest):
    if rag_chain is None:
        return {"error": "Model is still loading. Please try again shortly."}
    try:
        response = rag_chain.invoke(request.question)
        return {"answer": response}
    except Exception as e:
        return {"error": str(e)}