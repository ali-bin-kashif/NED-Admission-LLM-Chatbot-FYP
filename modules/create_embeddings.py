
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
# from langchain_community.vectorstores.pinecone import Pinecone
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.document_loaders import WebBaseLoader
import google.generativeai as genai

from langchain_pinecone import PineconeVectorStore

from pinecone import Pinecone
import os
from dotenv import load_dotenv

# Setting path for input data files
DATA_PATH = 'data/'

# Path for vectorstore to store text embeddings made from the data
DB_FAISS_PATH = 'vectorstore/db_faiss'


# Google Gemini API key setup
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

pinecone_api_key = os.getenv("PINECONE_API_KEY")
print(pinecone_api_key)


# Create vector database
def create_vector_db():
    
    # Connecting with Pinecone
    pc = Pinecone(pinecone_api_key)
    
    index = pc.Index('langchain-ned-data')
    
    # Load data from website
    website_loader = WebBaseLoader(['https://www.neduet.edu.pk/faculties_and_departments', 'https://www.neduet.edu.pk/academic_programmes', 'https://www.neduet.edu.pk/asrb', 'https://www.neduet.edu.pk/teaching_system', 'https://www.neduet.edu.pk/students_affairs', 'https://www.neduet.edu.pk/students_chapter_of_professional_bodies', 'https://www.neduet.edu.pk/contact-us'])
    website_loader.requests_kwargs = {'verify':False}
    
    civil_dept_web = WebBaseLoader(['https://ced.neduet.edu.pk/']).load()
    
    csit_dept_web = WebBaseLoader(['https://cct.neduet.edu.pk/research', 'https://cct.neduet.edu.pk/contact-us', 'https://cct.neduet.edu.pk/aboutus', 'https://cct.neduet.edu.pk/achievements', 'https://cis.neduet.edu.pk/' , 'https://cis.neduet.edu.pk/about_us', 'https://se.neduet.edu.pk/']).load()
    
    other_depts_web = WebBaseLoader(['https://eqd.neduet.edu.pk', 'https://end.neduet.edu.pk', 'https://ped.neduet.edu.pk']).load()
    
    electrical_depts_web = WebBaseLoader(['https://eed.neduet.edu.pk', 'https://eld.neduet.edu.pk/', 'https://tcd.neduet.edu.pk/', 'https://bmd.neduet.edu.pk/']).load()
    
    mechanical_manf_depts_web = WebBaseLoader(['https://med.neduet.edu.pk/', 'https://imd.neduet.edu.pk/', 'https://txd.neduet.edu.pk/', 'https://atd.neduet.edu.pk/']).load()
    
    arch_sci_depts = WebBaseLoader(['https://ard.neduet.edu.pk/', 'https://emd.neduet.edu.pk/', 'https://dph.neduet.edu.pk/aboutus', 'https://dcy.neduet.edu.pk/', 'https://dmt.neduet.edu.pk/', 'https://del.neduet.edu.pk/', 'https://des.neduet.edu.pk/']).load()
    
    
    
    web_doc = website_loader.load()
  

    # Load the PDF documents
    loader = DirectoryLoader(DATA_PATH,
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)

    documents = loader.load()
    
    docs = documents + web_doc + civil_dept_web + csit_dept_web + other_depts_web + electrical_depts_web + mechanical_manf_depts_web + arch_sci_depts
    
    print(len(docs))
    
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300,
                                                   chunk_overlap=100)
    texts = text_splitter.split_documents(docs)

    # Using Google Emebeddings
    # embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    
    # Using Open AI Embeddings
    embeddings = OpenAIEmbeddings(model='text-embedding-3-large')
    
    # Converting all the chunks into text embeddings (Converting text into vectors)
    # After text is converted into vectors, it can be used to many task like classifications etc.
    
    db = PineconeVectorStore.from_documents(texts, embeddings, index_name="langchain-ned-data")
    
    # Saving the embeddings in the vector store
    # db.save_local(DB_FAISS_PATH)
    print("Succesfully made and saved text embeddings!")

if __name__ == "__main__":
    create_vector_db()