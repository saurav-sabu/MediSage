from src.helper import load_pdf_file, text_splitting, initialize_embedding
from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore

load_dotenv()

extracted_data = load_pdf_file("data/medical_data.pdf")
chunks = text_splitting(extracted_data)
embedding = initialize_embedding()

pc = Pinecone()

index_name = "medisage"

pc.create_index(
    name=index_name,
    dimension=768, # Replace with your model dimensions
    metric="cosine", # Replace with your model metric
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    ) 
)

docsearch = PineconeVectorStore.from_documents(
    documents=chunks,
    embedding=embedding,
    index_name=index_name,
)