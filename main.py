from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from modules import models
from modules import chatbot_functions as chatbot
# import os
# from dotenv import load_dotenv
# import json

from modules import auth


    
#Fast API
app = FastAPI()

# Authorization Endpoints
@app.post("/register", response_model=models.User)
def register(user: models.User):
    existing_user = auth.get_user_from_db(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    auth.create_user_in_db(user.username, user.email, user.password)
    return user

@app.post("/token", response_model=models.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print(user)
    access_token = auth.create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=models.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# API endpoint (POST Request)
@app.post("/llm_on_cpu")
async def final_result(item: models.validation):
        print(chatbot.chat_history)
        response = chatbot.user_input(item.prompt)
        return response
    
@app.post("/load_create_chat")
async def sign_in(item: models.ChatInfo):

    user = auth.get_user_from_db(item.username)
    # global user_chat_details
    chatbot.user_chat_details = {
        'user_id' : user['id'],
        'chat_id' : item.chat_id
    }
    
    print(chatbot.user_chat_details)
    
    chat_exist = chatbot.chat_obj.does_chat_exist(chatbot.user_chat_details)
    print(chat_exist)
    if(chat_exist):
        chatbot.fetch_chat_history()
        return {"message": "Chat history fetched successfully",
            "user_id": user['id'],
            "chat_id": item.chat_id,
            'username': item.username}
    else:
        chatbot.chat_history=[]
        print(chatbot.chat_history)
        return {"message": "Chat created successfully",
            "user_id": user['id'],
            "chat_id": item.chat_id,
            'username': item.username}
    
    


