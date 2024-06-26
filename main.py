from fastapi import FastAPI
from modules import models
from modules import chatbot_functions as chatbot
import os
from dotenv import load_dotenv
import json


    
#Fast API
app = FastAPI()

# API endpoint (POST Request)
@app.post("/llm_on_cpu")
async def final_result(item: models.validation):
        print(chatbot.chat_history)
        response = chatbot.user_input(item.prompt)
        return response
    
@app.post("/user_sign_in")
async def sign_in(item: models.user_authentication):

    # global user_chat_details
    chatbot.user_chat_details = {
        'user_id' : item.user_id,
        'chat_id' : item.chat_id
    }
    
    print(chatbot.user_chat_details)
    
    chat_exist = chatbot.chat_obj.does_chat_exist(chatbot.user_chat_details)
    print(chat_exist)
    if(chat_exist):
        chatbot.fetch_chat_history()
    else:
        chatbot.chat_history=[]
        print(chatbot.chat_history)
    
    return {"message": "User signed in successfully", "user_id": item.user_id, "chat_id": item.chat_id}
