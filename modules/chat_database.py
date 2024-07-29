import mysql.connector
from mysql.connector import Error
import json
import os

# Fetching credentials from environment variables
host = os.getenv('DATABASE_HOST')
db_pass = os.getenv('DATABASE_PW')
db_user = os.getenv('DATABASE_USER')
db = os.getenv('DATABASE')

class ChatDatabase:
    """
    A class used to interact with the chat database.

    Attributes:
        host (str): Database host.
        user (str): Database user.
        password (str): Database password.
        database (str): Database name.
    """

    def __init__(self, host: str, user: str, password: str, database: str):
        """
        Initializes the ChatDatabase with connection parameters.

        Args:
            host (str): Database host.
            user (str): Database user.
            password (str): Database password.
            database (str): Database name.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def create_connection(self):
        """
        Creates and returns a database connection.

        Returns:
            mysql.connector.connection_cext.CMySQLConnection: Database connection object if successful, None otherwise.
        """
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error: {e}")
            return None

    def create_new_chat(self, user_id: int, chat_id: int, chat_history: list):
        """
        Creates a new chat in the database.

        Args:
            user_id (int): ID of the user.
            chat_id (int): ID of the chat.
            chat_history (list): History of the chat messages.
        """
        insert_query = """
        INSERT INTO chats (user_id, chat_id, chat_history)
        VALUES (%s, %s, %s)
        """
        chat_dict = {'chat_history': chat_history}
        chat_history_json = json.dumps(chat_dict)
        values = (user_id, chat_id, chat_history_json)
        
        connection = self.create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(insert_query, values)
                    connection.commit()
                    print("Chat created successfully")
            except Error as e:
                print(f"Error: {e}")
            finally:
                connection.close()
                print("Connection closed")

    def update_existing_chat(self, user_id: int, chat_id: int, chat_history: list):
        """
        Updates an existing chat in the database.

        Args:
            user_id (int): ID of the user.
            chat_id (int): ID of the chat.
            chat_history (list): Updated history of the chat messages.
        """
        update_query = """
        UPDATE chats
        SET chat_history = %s
        WHERE user_id = %s AND chat_id = %s
        """
        chat_dict = {'chat_history': chat_history}
        chat_history_json = json.dumps(chat_dict)
        values = (chat_history_json, user_id, chat_id)
        
        connection = self.create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(update_query, values)
                    connection.commit()
                    print("Chat updated successfully")
            except Error as e:
                print(f"Error: {e}")
            finally:
                connection.close()
                print("Connection closed")

    def delete_chat(self, user_id: int, chat_id: int):
        """
        Deletes a chat from the database.

        Args:
            user_id (int): ID of the user.
            chat_id (int): ID of the chat.
        """
        delete_query = """
        DELETE FROM chats
        WHERE user_id = %s AND chat_id = %s
        """
        values = (user_id, chat_id)
        
        connection = self.create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(delete_query, values)
                    connection.commit()
                    print("Chat deleted successfully")
            except Error as e:
                print(f"Error: {e}")
            finally:
                connection.close()
                print("Connection closed")

    def does_chat_exist(self, user_chat_ids: dict) -> bool:
        """
        Checks if a chat exists in the database.

        Args:
            user_chat_ids (dict): Dictionary containing 'user_id' and 'chat_id'.

        Returns:
            bool: True if chat exists, False otherwise.
        """
        fetch_query = """
        SELECT chat_history
        FROM chats
        WHERE user_id = %s AND chat_id = %s
        """
        values = (user_chat_ids['user_id'], user_chat_ids['chat_id'])
        
        connection = self.create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(fetch_query, values)
                    result = cursor.fetchone()
                    return result is not None
            except Error as e:
                print(f"Error: {e}")
                return False
            finally:
                connection.close()
                print("Connection closed")

    def fetch_chat_data(self, user_chat_ids: dict) -> list:
        """
        Fetches chat history from the database.

        Args:
            user_chat_ids (dict): Dictionary containing 'user_id' and 'chat_id'.

        Returns:
            list: Chat history if found, empty list otherwise.
        """
        fetch_query = """
        SELECT chat_history
        FROM chats
        WHERE user_id = %s AND chat_id = %s
        """
        values = (user_chat_ids['user_id'], user_chat_ids['chat_id'])
        
        connection = self.create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(fetch_query, values)
                    chat = cursor.fetchone()
                    if chat:
                        chat_json = chat[0]
                        chat_dict = json.loads(chat_json)
                        return chat_dict['chat_history']
                    else:
                        return []
            except Error as e:
                print(f"Error: {e}")
                return []
            finally:
                connection.close()
                print("Connection closed")

if __name__ == "__main__":
    chat = ChatDatabase(host, db_user, db_pass, db)
    print(chat.host)
