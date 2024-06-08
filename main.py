# Importing libs and modules

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
import google.generativeai as genai

from langchain_community.vectorstores.faiss import FAISS

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage

from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import json

from chat_database import ChatDatabase

# Setting Google API Key
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
groq_api_key=os.getenv('GROQ_API_KEY')

# Path of vectore database
DB_FAISS_PATH = 'vectorstore/db_faiss'

# Initialize Chat database object
chat_obj = ChatDatabase(
    'chatbot-user-chats-data.c32iyywau6nz.ap-south-1.rds.amazonaws.com',
    'admin',
    'alihamza123',
    'chat_history'
)

user_chat_details = {}
chat_history = []
print(chat_history)

def fetch_chat_history():
    global chat_history
    chat_history= chat_obj.fetch_chat_data(user_chat_details)
    print(chat_history)


#Loading the model
def load_llm():
    # llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=1, max_output_tokens=2000)
    llm=ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192", temperature=0.5)
    return llm



def history_aware_retriever(retriever , llm):
    
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

# Setting QA chain
def get_conversational_chain(history_aware_retriever, llm):

    
    qa_system_prompt = """You are an assistant of our NED University for question-answering tasks to help students and users for their questions and queries. \
    Use the following pieces of context to answer the question. \
    If you don't know the answer, just say that you don't know. Don't try to make wrong answers \
    Don't give answer to irrelevant or abusive questions and words, just appoligize\
    Keep the answer concise and well formatted with a professional and friendly tone.\
    Always remember that your scope is limited to NED University and guiding students, if you get question out of this scope, command the user the search this on Goolge, don't try to answer it by yourself.\
    When user asks information of department(s) always tell them to visit the department website and ask them if they want the website link.\
    If users ask to conduct or generate a mockup or sample test paper, make a detailed sample test with all the relevant sections.
    Always welcome and appreciate for reaching out and offer students more help in the end and call to action and include contact or email if possible.

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

# User input function
def user_input(user_question):
    
    # Set google embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    
    # Loading saved vectors from local path
    db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever()
    
    llm = load_llm()
    
    history_retriever = history_aware_retriever(retriever, llm)
    
    rag_chain = get_conversational_chain(history_retriever, llm)
    
    response = rag_chain.invoke({"input": user_question, "chat_history": chat_history})
    # chat_history.extend([HumanMessage(content=user_question), response["answer"]])
    chat_history.extend([user_question, response["answer"]])
    print(chat_history)
    if(chat_obj.does_chat_exist(user_chat_details)):
        
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
    
    
        
    
    return response

#Pydantic object
class validation(BaseModel):
    prompt: str
    
class user_authentication(BaseModel):
    user_id: int
    chat_id: int
    
#Fast API
app = FastAPI()

# API endpoint (POST Request)
@app.post("/llm_on_cpu")
async def final_result(item: validation):
        print(chat_history)
        response = user_input(item.prompt)
        return response
    
@app.post("/user_sign_in")
async def sign_in(item: user_authentication):

    global user_chat_details
    user_chat_details = {
        'user_id' : item.user_id,
        'chat_id' : item.chat_id
    }
    
    
    if(chat_obj.does_chat_exist(user_chat_details)):
        fetch_chat_history()
    else:
        global chat_history
        chat_history=[]
        print(chat_history)
    
    return {"message": "User signed in successfully", "user_id": item.user_id, "chat_id": item.chat_id}
