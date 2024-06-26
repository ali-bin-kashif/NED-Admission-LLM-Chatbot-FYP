from pydantic import BaseModel

#Pydantic objects

class validation(BaseModel):
    prompt: str
    
class user_authentication(BaseModel):
    user_id: int
    chat_id: int