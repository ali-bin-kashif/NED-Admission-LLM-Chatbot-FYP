
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.document_loaders import WebBaseLoader
import google.generativeai as genai
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

# Create vector database
def create_vector_db():
    
    # Load data from website
    website_loader = WebBaseLoader(['https://cct.neduet.edu.pk/research', 'https://en.wikipedia.org/wiki/NED_University_of_Engineering_%26_Technology', 'https://cct.neduet.edu.pk/contact-us', 'https://cct.neduet.edu.pk/aboutus', 'https://cct.neduet.edu.pk/achievements'])
    
    web_doc = website_loader.load()

    # Load the PDF documents
    loader = DirectoryLoader(DATA_PATH,
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)

    documents = loader.load()
    
    docs = documents + web_doc
    
    print(len(docs))
    
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                   chunk_overlap=200)
    texts = text_splitter.split_documents(docs)

    # Using hugging face embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    
    # Converting all the chunks into text embeddings (Converting text into vectors)
    # After text is converted into vectors, it can be used to many task like classifications etc.
    db = FAISS.from_documents(texts, embeddings)
    
    # Saving the embeddings in the vector store
    db.save_local(DB_FAISS_PATH)
    print("Succesfully made and saved text embeddings!")

if __name__ == "__main__":
    create_vector_db()