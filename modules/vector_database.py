from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
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

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

# Configure Google Gemini API
genai.configure(api_key=google_api_key)

# Print Pinecone API key for verification
print(pinecone_api_key)

# Initialize Pinecone
pc = Pinecone(pinecone_api_key)
index = pc.Index('langchain-ned-data')

def create_vector_db():
    """
    Creates a vector database by loading data from websites and PDFs, 
    generating text embeddings, and saving them in a Pinecone vector store.
    """
    # Load data from various websites
    website_loader = WebBaseLoader([
        'https://www.neduet.edu.pk/faculties_and_departments', 
        'https://www.neduet.edu.pk/academic_programmes', 
        'https://www.neduet.edu.pk/asrb', 
        'https://www.neduet.edu.pk/teaching_system', 
        'https://www.neduet.edu.pk/students_affairs', 
        'https://www.neduet.edu.pk/students_chapter_of_professional_bodies', 
        'https://www.neduet.edu.pk/contact-us'
    ])
    website_loader.requests_kwargs = {'verify': False}
    
    # Load data from specific department websites
    civil_dept_web = WebBaseLoader(['https://ced.neduet.edu.pk/']).load()
    csit_dept_web = WebBaseLoader([
        'https://cct.neduet.edu.pk/research', 
        'https://cct.neduet.edu.pk/contact-us', 
        'https://cct.neduet.edu.pk/aboutus', 
        'https://cct.neduet.edu.pk/achievements', 
        'https://cis.neduet.edu.pk/' , 
        'https://cis.neduet.edu.pk/about_us', 
        'https://se.neduet.edu.pk/'
    ]).load()
    other_depts_web = WebBaseLoader([
        'https://eqd.neduet.edu.pk', 
        'https://end.neduet.edu.pk', 
        'https://ped.neduet.edu.pk'
    ]).load()
    electrical_depts_web = WebBaseLoader([
        'https://eed.neduet.edu.pk', 
        'https://eld.neduet.edu.pk/', 
        'https://tcd.neduet.edu.pk/', 
        'https://bmd.neduet.edu.pk/'
    ]).load()
    mechanical_manf_depts_web = WebBaseLoader([
        'https://med.neduet.edu.pk/', 
        'https://imd.neduet.edu.pk/', 
        'https://txd.neduet.edu.pk/', 
        'https://atd.neduet.edu.pk/'
    ]).load()
    arch_sci_depts = WebBaseLoader([
        'https://ard.neduet.edu.pk/', 
        'https://emd.neduet.edu.pk/', 
        'https://dph.neduet.edu.pk/aboutus', 
        'https://dcy.neduet.edu.pk/', 
        'https://dmt.neduet.edu.pk/', 
        'https://del.neduet.edu.pk/', 
        'https://des.neduet.edu.pk/'
    ]).load()
    
    # Load main website data
    web_doc = website_loader.load()
    
    # Load PDF documents
    loader = DirectoryLoader(DATA_PATH, glob='*.pdf', loader_cls=PyPDFLoader)
    documents = loader.load()
    
    # Combine all loaded documents
    docs = documents + web_doc + civil_dept_web + csit_dept_web + other_depts_web + electrical_depts_web + mechanical_manf_depts_web + arch_sci_depts
    print(len(docs))
    
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
    texts = text_splitter.split_documents(docs)

    # Generate text embeddings using OpenAI Embeddings
    embeddings = OpenAIEmbeddings(model='text-embedding-3-large')
    
    # Create a Pinecone vector store from the documents and embeddings
    db = PineconeVectorStore.from_documents(texts, embeddings, index_name="langchain-ned-data")
    
    # Save the embeddings in the vector store
    # db.save_local(DB_FAISS_PATH)
    print("Successfully made and saved text embeddings!")

def delete_all_embeddings():
    """
    Deletes all embeddings from the Pinecone index.
    """
    status = index.delete(delete_all=True, namespace="")
    
    if status is not None:
        print("Deleted!")
    
def delete_file_embeddings(file_name: str):
    """
    Deletes a file embeddings from the Pinecone index with meta-data filtering.
    """
    status = index.delete(
        filter={
            "filename" : file_name
        }
    )
    
    if status == {}:
        print("Embeddings of file:" + file_name + " deleted successfully!")
    else:
        print(file_name + ": File not found")
    

def add_docs(documents):
    """
    Adds new documents to the Pinecone vector store.
    """
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    print(len(texts))
    
    # Generate text embeddings using OpenAI Embeddings
    embeddings = OpenAIEmbeddings(model='text-embedding-3-large')
    
    # Initialize Pinecone vector store and add documents
    vectorstore = PineconeVectorStore(embedding=embeddings, index_name="langchain-ned-data")
    vectors = vectorstore.add_documents(texts)
    
    if vectors is not None:
        print('Vectors Embeddings created successfully!')
    else:
        print('Failed creating embeddings!')
    
    
if __name__ == "__main__":
    # Uncomment the following lines to execute the desired functions
    # create_vector_db()
    # delete_all_embeddings()
    add_docs()
    