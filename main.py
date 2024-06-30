from fastapi import FastAPI, Depends,Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from modules import models
from modules import chatbot_functions as chatbot
from mysql.connector import Error
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

@app.post("/login", response_model=models.Token)

def login_for_access_token(login_data: models.LoginInfo):
    user = auth.authenticate_user(login_data.email, login_data.password)
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
async def final_result(item: models.validation, authorization: str = Header(None)):

        if authorization is None or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

        access_token = authorization.split("Bearer ")[1]
        print(access_token)
        user = auth.get_current_user(access_token)
        
        if not user:
            raise HTTPException(status_code=404, detail="User Not found")
        
        print(chatbot.chat_history)
        response = chatbot.user_input(item.prompt)
        return response
        
    
def get_authorization_header(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    return authorization.split("Bearer ")[1]

@app.post("/load_create_chat")
async def sign_in(item: models.ChatInfo, access_token: str = Depends(get_authorization_header)):
    print(access_token)

    user = auth.get_current_user(access_token)
    # global user_chat_details
    chatbot.user_chat_details = {
        'user_id': user['id'],
        'chat_id': item.chat_id
    }
    
    print(chatbot.user_chat_details)
    
    try:
        chat_exist = chatbot.chat_obj.does_chat_exist(chatbot.user_chat_details)
        print(chat_exist)
        if chat_exist:
            chatbot.fetch_chat_history()
            return {
                "message": "Chat history fetched successfully",
                "user_id": user['id'],
                "chat_id": item.chat_id,
                'username': user['username'],
                'success': True
            }
        else:
            chatbot.chat_history = []
            print(chatbot.chat_history, 'hi')
            return {
                "message": "Chat created successfully",
                "user_id": user['id'],
                "chat_id": item.chat_id,
                'username': user['username'],
                'success': True
            }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "success": False,
            "message": "An error has occurred, please try again."
        }
        
        
    


