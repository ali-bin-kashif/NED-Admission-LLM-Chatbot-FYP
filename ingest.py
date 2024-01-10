# Importing libs and modules
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Setting path for input data files
DATA_PATH = 'data/'

# Path for vectorstore to store text embeddings made from the data
DB_FAISS_PATH = 'vectorstore/db_faiss'

# Create vector database
def create_vector_db():
    
    # Load the PDF documents
    loader = DirectoryLoader(DATA_PATH,
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)

    documents = loader.load()
    
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=256,
                                                   chunk_overlap=32)
    texts = text_splitter.split_documents(documents)

    # Using hugging face embeddings
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                       model_kwargs={'device': 'cpu'})
    
    # Converting all the chunks into text embeddings (Converting text into vectors)
    # After text is converted into vectors, it can be used to many task like classifications etc.
    db = FAISS.from_documents(texts, embeddings)
    
    # Saving the embeddings in the vector store
    db.save_local(DB_FAISS_PATH)

if __name__ == "__main__":
    create_vector_db()

