# Import necessary libraries and modules
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
# import google.generativeai as genai
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from modules.chat_database import ChatDatabase, host, db_pass, db_user, db
from dotenv import load_dotenv
import os

from langchain_pinecone import PineconeVectorStore

from pinecone import Pinecone

import asyncio

# Load environment variables from .env file
load_dotenv()

# Configure Google Generative AI API key
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set Groq API key
groq_api_key = os.getenv('GROQ_API_KEY')
open_ai_key = os.getenv('OPEN_AI_KEY')
pinecone_api_key = os.getenv('PINECONE_API_KEY')


# Connecting with Pinecone


# Path to the FAISS vector database
DB_FAISS_PATH = 'vectorstore/db_faiss'

# Initialize ChatDatabase object
chat_obj = ChatDatabase(host, db_user, db_pass, db)

# Initialize user chat details and history
user_chat_details = {}
chat_history = []
print(chat_history)

def fetch_chat_history():
    """
    Fetches the chat history from the database for the given user details.
    """
    global chat_history
    chat_history = chat_obj.fetch_chat_data(user_chat_details)
    print(chat_history)
    
    
def convert_to_array_of_dicts(chat_history):
    """
    Function for converting array of chat history into dictionary with role as keys (Human and Chatbot) and content as value.
    """
    chat_array = []
    
    for i in range(0, len(chat_history), 2):
        human_message = chat_history[i]
        chatbot_message = chat_history[i + 1] if i + 1 < len(chat_history) else ""
        
        chat_array.append({"role": "human", "content": human_message})
        if chatbot_message:
            chat_array.append({"role": "chatbot", "content": chatbot_message})
    
    return chat_array

def load_llm():
    """
    Loads the language model for the chatbot.
    
    Returns:
        llm (ChatGroq): The loaded language model.
    """
    # Chat Groq Model
    # llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192", temperature=0.5)
    
    # Open AI Model
    llm = ChatOpenAI(model='gpt-4o', temperature=0.5, api_key=open_ai_key)
    return llm

def history_aware_retriever(retriever, llm):
    """
    Creates a history-aware retriever for contextualizing user questions.
    
    Args:
        retriever: The retriever object for fetching documents.
        llm: The language model object.
    
    Returns:
        history_aware_retriever: A retriever that considers chat history for context.
    """
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
        llm, retriever, contextualize_q_prompt
    )
    
    return history_aware_retriever

def get_conversational_chain(history_aware_retriever, llm):
    """
    Sets up the question-answering chain with history-aware retriever.
    
    Args:
        history_aware_retriever: The history-aware retriever object.
        llm: The language model object.
    
    Returns:
        rag_chain: The retrieval-augmented generation chain for conversational QA.
    """
    qa_system_prompt = """You are an assistant of our NED University for question-answering tasks to help students and users for their questions and queries. \
    Use the following pieces of context to answer the question. \
    If you don't know the answer, just say that you don't know. Don't try to make wrong answers \
    Don't give answer to irrelevant or abusive questions and words, just apologize\
    Keep the answer concise and well formatted with a professional and friendly tone.\
    Always remember that your scope is limited to NED University and guiding students, if you get question out of this scope, command the user to search this on the internet, don't try to answer it by yourself.\
    When user asks information of department(s) always tell them to visit the department website and ask them if they want the website link.\
    If users ask to conduct or generate a mockup or sample test paper, make a detailed sample test with all the relevant sections.\
    Check the language of the prompt and try to answer in that language.\
    If user ask about some person or faculty member, always start by their introduction, what department and position they belong to.\
    Always welcome and appreciate for reaching out and offer students more help in the end and call to action and include contact or email or relevant website link(s) if possible.\

    {context}"""
    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    return rag_chain

async def update_chat_history(user_question, answer):
    chat_history.extend([user_question, answer])
    print(chat_history)
    
    # Check and update the database asynchronously, if applicable
    if chat_obj.does_chat_exist(user_chat_details):
        chat_obj.update_existing_chat(
            user_chat_details['user_id'],
            user_chat_details['chat_id'],
            chat_history
        )
    else:
        chat_obj.create_new_chat(
            user_chat_details['user_id'],
            user_chat_details['chat_id'],
            chat_history
        )

async def user_input(user_question):
    """
    Asynchronously processes the user input, retrieves vector embeddings, generate response,
    and updates the chat history asynchronously.
    
    Args:
        user_question (str): The question input by the user.
    
    Returns:
        response: The response from the language model.
    """
    # Set OPEN AI embeddings
    embeddings = OpenAIEmbeddings(model='text-embedding-3-large')
    
    # Asynchronously create the vector store and retriever
    db = PineconeVectorStore(index_name="langchain-ned-data", embedding=embeddings)
    retriever = db.as_retriever()
    
    # Load the language model
    llm = load_llm()
    
    # Create a history-aware retriever
    history_retriever = history_aware_retriever(retriever, llm)
    
    # Set up the conversational QA chain
    rag_chain = get_conversational_chain(history_retriever, llm)
    
    # Asynchronously invoke the chain with user input and chat history
    response = rag_chain.invoke({"input": user_question, "chat_history": chat_history})
    
    # Asynchronously update chat history
    asyncio.create_task(update_chat_history(user_question, response["answer"]))
    
    return response

# def user_input(user_question):
#     """
#     Processes the user input, retrieves vector embeddings, generate response,
#     and updates the chat history.
    
#     Args:
#         user_question (str): The question input by the user.
    
#     Returns:
#         response: The response from the language model.
#     """
#     # Set Google embeddings
#     # embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
#     # Set OPEN AI embeddings
#     embeddings = OpenAIEmbeddings(model='text-embedding-3-large')
    
#     # # Load saved vectors from the local path
#     # pc = Pinecone(pinecone_api_key)
    
#     # index = pc.Index('langchain-ned-data')
    
#     # index.query()
#     # db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    
#     db = PineconeVectorStore(index_name = "langchain-ned-data", embedding = embeddings)
#     retriever = db.as_retriever()
    
#     # Load the language model
#     llm = load_llm()
    
#     # Create a history-aware retriever
#     history_retriever = history_aware_retriever(retriever, llm)
    
#     # Set up the conversational QA chain
#     rag_chain = get_conversational_chain(history_retriever, llm)
    
#     # Invoke the chain with user input and chat history
#     response = rag_chain.invoke({"input": user_question, "chat_history": chat_history})
    
#     # Update chat history
#     chat_history.extend([user_question, response["answer"]])
#     print(chat_history)
    
#     # Check if chat exists in the database and update or create new chat accordingly
#     if chat_obj.does_chat_exist(user_chat_details):
#         chat_obj.update_existing_chat(
#             user_chat_details['user_id'],
#             user_chat_details['chat_id'],
#             chat_history
#         )
#     else:
#         chat_obj.create_new_chat(
#             user_chat_details['user_id'],
#             user_chat_details['chat_id'],
#             chat_history
#         )
    
#     return response
