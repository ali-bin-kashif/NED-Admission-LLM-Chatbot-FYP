# Importing libs and modules
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains.question_answering import load_qa_chain
from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Setting Google API Key
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Path of vectore database
DB_FAISS_PATH = 'vectorstore/db_faiss'


# Prompt template
custom_prompt_template = """
    Use the following pieces of information to answer the user's question.\n
    Context: {context}
    Question: {question}
     
    Try to give the best and correct answer only.
    Also try to add some your own wordings the describe the answer.
    Helpful Answer:
"""

def set_custom_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt



#Loading the model
def load_llm():
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.6)
    return llm


# Setting QA chain
def get_conversational_chain():

    prompt = set_custom_prompt()
    
    llm = load_llm()
    chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)

    return chain

# User input function
def user_input(user_question):
    
    # Set google embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    
    # Loading saved vectors from local path
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    docs = db.similarity_search(user_question)
    
    chain = get_conversational_chain()
    
    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)

    return response

#Pydantic object
class validation(BaseModel):
    prompt: str
#Fast API
app = FastAPI()

# API endpoint (POST Request)
@app.post("/llm_on_cpu")
async def final_result(item: validation):
        response = user_input(item.prompt)
        return response