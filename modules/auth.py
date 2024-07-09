import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt
import mysql.connector
from mysql.connector import Error

# Fetching database credentials from environment variables
DB_HOST = os.getenv('DATABASE_HOST')
DB_PASSWORD = os.getenv('DATABASE_PW')
DB_USER = os.getenv('DATABASE_USER')
DB_NAME = os.getenv('DATABASE')

# Secret key to encode and decode JWT tokens
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# OAuth2 password flow for obtaining the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=2880)):
    """
    Creates a JWT token with the given data and expiration delta.

    Args:
        data (dict): Data to be encoded in the token.
        expires_delta (timedelta, optional): Expiration time delta for the token. Defaults to 2880 minutes.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})  # Add expiration time to the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode the JWT
    return encoded_jwt



def get_user_from_db(username: str):
    """
    Retrieves a user from the database by username.

    Args:
        username (str): Username to search for.

    Returns:
        dict: User record if found, else None.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))  # Query to fetch user by username
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None




def get_user_from_db_email(email: str):
    """
    Retrieves a user from the database by email.

    Args:
        email (str): Email to search for.

    Returns:
        dict: User record if found, else None.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))  # Query to fetch user by email
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None




def create_user_in_db(username: str, email: str, password: str):
    """
    Creates a new user in the database.

    Args:
        username (str): Username for the new user.
        email (str): Email for the new user.
        password (str): Password for the new user.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))  # Insert new user
        connection.commit()
        print(f'User Registered: {username}, {email}')
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return e

def authenticate_user(email: str, password: str):
    """
    Authenticates a user by email and password.

    Args:
        email (str): User's email.
        password (str): User's password.

    Returns:
        dict: User record if authentication is successful, False otherwise.
    """
    user = get_user_from_db_email(email)
    if not user or user["password"] != password:  # Check if user exists and password matches
        return False
    return user




def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Gets the current user based on the JWT token.

    Args:
        token (str): JWT token.

    Returns:
        dict: User record.

    Raises:
        HTTPException: If the token is invalid or user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decode the JWT token
        username: str = payload.get("sub")
        if username is None:  # Check if username is present in the payload
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user_from_db(username)  # Fetch the user from the database
    if user is None:  # Check if user exists
        raise credentials_exception
    return user
