from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

def load_pdf_file(file_path):
    documents = PyPDFLoader(file_path).load()
    return documents

def text_splitting(extracted_data):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    chunks = splitter.split_documents(extracted_data)
    return chunks

def initialize_embedding():
    embedding = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    return embedding