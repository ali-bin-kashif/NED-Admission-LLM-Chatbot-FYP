# Importing necessary modules and libraries
from typing import Annotated

from fastapi import APIRouter, File, UploadFile, HTTPException, Body
from fastapi.responses import HTMLResponse

import fitz  # PyMuPDF for PDF handling
import os

from langchain_community.document_loaders import WebBaseLoader
from langchain.docstore.document import Document

import boto3
from botocore.exceptions import NoCredentialsError

from modules import vector_database
from modules import models

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
BUCKET_NAME = os.getenv('BUCKET_NAME')

# Initializing AWS Client for S3 Buckets
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Initialize Router
router = APIRouter(
    prefix='/chatbot_data',
    tags=['Chatbot knowledge base endpoints']
)

@router.post("/uploadfiles")
async def upload_files(files: Annotated[list[UploadFile], File()]):
    """
    Uploads multiple files to an S3 bucket and extracts text content from PDFs.

    Parameters:
    - files: List of files to be uploaded.

    Returns:
    - dict: A dictionary containing URLs of the uploaded files and a success message.
    """
    file_urls = []
    docs = []

    for file in files:
        # Read the file content
        pdf_content = await file.read()
        
        try:
            # Upload file to S3
            file_path = file.filename
            s3_client.upload_fileobj(file.file, BUCKET_NAME, file_path)
            file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_path}"
            file_urls.append(file_url)
        except NoCredentialsError:
            return {"error": "AWS credentials not available"}
        
        # Extract text content from the PDF
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""
        for page in pdf_document:
            text += page.get_text()
        
        # Create a Document object for LangChain
        doc = Document(page_content=text, metadata={"filename": file.filename})
        docs.append(doc)
    
    # Add documents to vector database
    vector_database.add_docs(docs)
    
    return {"file_urls": file_urls, "message": "Files uploaded to S3 successfully"}

@router.post("/extract-and-store-sites")
async def extract_and_store_webpages(urls: models.webURLS):
    """
    Extracts content from a list of URLs and stores them in the vector database.

    Parameters:
    - urls (list): List of URLs from which to extract content.

    Returns:
    - dict: A dictionary containing a message indicating success.
    """
    urls = urls.urls
    print(urls)
    try:
        docs = []
        for url in urls:
            # Use a web loader to fetch content from URL
            web_loader = WebBaseLoader(url)
            content = web_loader.load()
            docs.extend(content)
        
        # Adding documents to Pinecone vector store
        vector_database.add_docs(docs)
        
        return {"message": "Content extracted and stored successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-all-files")
async def get_all_files_s3():
    """
    Retrieves all files from the S3 bucket.

    Returns:
    - dict: A dictionary containing the list of files and a success message.
    """
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' not in response:
            return {"message": "No files found in the bucket"}
        
        files = [
            {
                'File': item['Key'],
                'LastModified': item['LastModified'],
                'Size': item['Size'],
                'StorageClass': item['StorageClass'],
            }
            for item in response['Contents']
        ]

        return {"files": [item['Key'] for item in response['Contents']], "message": "Files fetched successfully"}
    except NoCredentialsError:
        return {"error": "AWS credentials not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-all-files")
async def delete_all_files():
    """
    Deletes all files from the S3 bucket and their embeddings from the vector database.

    Returns:
    - dict: A dictionary containing the list of deleted files and a success message.
    """
    try:
        # List all files in the S3 bucket
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' not in response:
            return {"message": "No files found in the bucket"}

        files_to_delete = [{'Key': item['Key']} for item in response['Contents']]

        # Batch delete operation
        delete_response = s3_client.delete_objects(
            Bucket=BUCKET_NAME,
            Delete={'Objects': files_to_delete}
        )

        deleted_files = [item['Key'] for item in delete_response.get('Deleted', [])]
        
        # Delete all embeddings from the vector database
        vector_database.delete_all_embeddings()
        
        return {"deleted_files": deleted_files, "message": "Files deleted successfully"}
    except NoCredentialsError:
        return {"error": "AWS credentials not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-file")
async def delete_file(file: models.FileName):
    """
    Deletes a specific file from the S3 bucket and its embeddings from the vector database.

    Parameters:
    - file (models.FileName): The name of the file to be deleted.

    Returns:
    - dict: A message indicating the status of the deletion operation.
    """
    try:
        # Delete the file from the S3 bucket
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file.file_name)
        
        # Delete vector embeddings with meta_data filtering
        # vector_database.delete_file_embeddings(file.file_name)
        
        return {"message": f"File '{file.file_name}' deleted successfully from S3."}
    except NoCredentialsError:
        return {"error": "AWS credentials not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
# @router.get("/")
# async def main():
#     content = """
# <body>
# <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
# <input name="files" type="file" multiple>
# <input type="submit">
# </form>
# </body>
#     """
#     return HTMLResponse(content=content)
