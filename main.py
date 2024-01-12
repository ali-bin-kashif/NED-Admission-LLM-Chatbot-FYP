# Importing libs and modules
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains.question_answering import load_qa_chain
# from langchain_community.llms.ctransformers import CTransformers
# from langchain.chains import RetrievalQA
from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Path of vectore database
DB_FAISS_PATH = 'vectorstore/db_faiss'


# Prompt template
custom_prompt_template = """
    Use the following pieces of information to answer the user's question.\n\n
    Context: {context}
    Question: {question}
     
    Try your best to give the answer. If you can't find the answer, say this "Sorry I can't help you on this query, Please see the guidelines and FAQs on the following link: https://www.neduet.edu.pk/admission, or contact administrator if you are facing problems".
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
    # Load the locally downloaded model here
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.6)
    return llm

def get_conversational_chain():

    prompt = set_custom_prompt()
    
    llm = load_llm()
    chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)

    return chain

#QA Model Function
def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    docs = db.similarity_search(user_question)
    
    chain = get_conversational_chain()
    
    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=False)

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