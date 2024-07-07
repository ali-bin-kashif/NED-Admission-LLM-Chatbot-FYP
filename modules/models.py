from pydantic import BaseModel

#Pydantic objects

class validation(BaseModel):
    prompt: str
    
class user_authentication(BaseModel):
    user_id: int
    chat_id: str
    
class User(BaseModel):
    username: str
    email : str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatInfo(BaseModel):
    chat_id: str
    
class LoginInfo(BaseModel):
    email: str
    password: str