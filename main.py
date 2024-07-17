from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware

from modules import models
from modules import chatbot_functions as chatbot
from modules import auth
from routers import vectordb_s3_endpoints

# FastAPI object
app = FastAPI(
    title="FYP RAG Chatbot FastAPI",
    summary="This is the backend of our final year project of university, which a chatbot for university admissions using LLM and RAG. The bot is powered by Langchain and FastAPI. The UI and frontend is developed in Next.js."
)

# Include vectordb and AWS S3 Buckets router
app.include_router(vectordb_s3_endpoints.router)

# Bearer token authentication scheme
auth_scheme = HTTPBearer()

# Configuring FastAPI CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Authorization Endpoints

@app.post("/register")
def register(user: models.User):
    """
    Endpoint for user registration.
    """
    try:
        existing_user = auth.get_user_from_db(user.username)
        if existing_user:  # Check if the username is already registered
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False, "message": "Username already registered"},
            )
        # Create a new user in the database
        response = auth.create_user_in_db(user.username, user.email, user.password)
        print(response)
        if response is None:
            return {
            "success": True,
            "detail": "User registered successfully.",
            "username": user.username,
            "email": user.email
            }
        else:
            return{
                "success": False,
                "detail": "Username or email already exist.",
                "error" : response
            }
 
        
    except HTTPException as http_exc:
        # Handle specific HTTP exceptions
        raise http_exc
    except (auth.DatabaseError, auth.ValidationError) as db_exc:
        # Handle known errors from the auth module
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(db_exc)},
        )
    except Exception as exc:
        # Catch all other exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": "An unexpected error occurred"},
        )


@app.post("/login")
def login_for_access_token(login_data: models.LoginInfo):
    """
    Endpoint for user login. Returns an access token if credentials are valid.
    """
    user = auth.authenticate_user(login_data.email, login_data.password)
    if not user:  # Check if the user credentials are valid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Incorrect username or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Generate an access token for the authenticated user
    access_token = auth.create_access_token(data={"sub": user["username"]})
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
        "email": user["email"]
    }



@app.get("/users/me", response_model=models.User)
def read_users_me(authorization: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """
    Endpoint to get the current logged-in user's information.
    """
    current_user = auth.get_current_user(authorization.credentials)  # Get the current user from the token
    return current_user



# API endpoint (POST Request)

@app.post("/llm_on_cpu")
def final_result(item: models.validation, authorization: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """
    Endpoint to process user input through a chatbot and return the response.
    """
    access_token = authorization.credentials
    if authorization is None:  # Check if the authorization header is missing or invalid
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    user = auth.get_current_user(access_token)  # Get the current user from the token
    if not user:  # Check if the user is found
        raise HTTPException(status_code=404, detail="User Not found")
    
    response = chatbot.user_input(item.prompt)  # Process the user input through the chatbot
    return response



@app.post("/load_create_chat")
async def sign_in(item: models.ChatInfo, authorization: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """
    Endpoint to load or create a chat and fetch chat history if it exists.
    """
    token = authorization.credentials
    if authorization is None:  # Check if the authorization header is missing or invalid
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    user = auth.get_current_user(token)  # Get the current user from the token
    chatbot.user_chat_details = {
        'user_id': user['id'],
        'chat_id': item.chat_id
    }

    try:
        chat_exist = chatbot.chat_obj.does_chat_exist(chatbot.user_chat_details)  # Check if the chat exists
        if chat_exist:
            chatbot.fetch_chat_history()  # Fetch the chat history
            chat_conversation = chatbot.convert_to_array_of_dicts(chatbot.chat_history)  # Convert chat history to array of dicts
            return {
                'success': True,
                "message": "Chat history fetched successfully",
                "user_id": user['id'],
                "chat_id": item.chat_id,
                'username': user['username'],
                "chat_history": chat_conversation
            }
        else:
            chatbot.chat_history = []  # Initialize an empty chat history
            return {
                "message": "Chat created successfully",
                "user_id": user['id'],
                "chat_id": item.chat_id,
                'username': user['username'],
                'success': True
            }
    except Exception as e:  # Handle any exceptions that occur
        return {
            "success": False,
            "message": "An error has occurred, please try again.",
            "Error": str(e)
        }


# Admin Panel Endpoints

