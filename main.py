from fastapi import FastAPI, Depends,Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from modules import models
from modules import chatbot_functions as chatbot
from mysql.connector import Error
# import os
# from dotenv import load_dotenv
# import json

from modules import auth

#Fast API object
app = FastAPI()

# Configuring FastAPI CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authorization Endpoints
@app.post("/register")
def register(user: models.User):
        existing_user = auth.get_user_from_db(user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False,"message":"Username already registered"},
            )
        auth.create_user_in_db(user.username, user.email, user.password)
        return {"success":True,
                "detail" : "User registered successfully.",
                "username": user.username,
                "email": user.email}
        

@app.post("/login")
def login_for_access_token(login_data: models.LoginInfo):
    
        user = auth.authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"success": False, "message":"Incorrect username or password"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        print(user)
        access_token = auth.create_access_token(data={"sub": user["username"]})
        return {"success" : True,
                "access_token": access_token,
                "token_type": "bearer",
                "username" : user["username"],
                "email" : user["email"]}
        

@app.get("/users/me", response_model=models.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# API endpoint (POST Request)
@app.post("/llm_on_cpu")
def final_result(item: models.validation, authorization: str = Header(None)):

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
        raise HTTPException(status_code=401, detail={"success":False ,"message":"Authorization header missing or invalid"})
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
            "message": "An error has occurred, please try again.",
            "Error" : e
        }
        
        
    


