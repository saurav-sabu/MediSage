from flask import Flask, request, jsonify, render_template
from src.helper import *
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from src.prompt import *
from langchain_core.messages import *
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

embedding = initialize_embedding()

docsearch = PineconeVectorStore.from_existing_index(
    index_name="medisage",
    embedding=embedding
)

retriever = docsearch.as_retriever(search_type="similarity",search_kwargs={"k":3})

chat_history = []

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    model, retriever, contextualize_q_prompt
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(model,prompt)
rag_chain = create_retrieval_chain(history_aware_retriever,question_answer_chain)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask",methods=["GET","POST"])
def ask():
    if request.method == "POST":
        question = request.form["chatInput"]
        response = rag_chain.invoke({"input": question,"chat_history":chat_history})
        chat_history.extend([HumanMessage(content=question), response["answer"]])
        
        # Extract the actual response text
        # Adjust this based on your exact response structure
        response_text = response.get('answer', str(response))
        
        return jsonify({"response": response_text})
    return jsonify({"response": "Please send a POST request with a question"})


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080,debug=True)