import mysql.connector
from mysql.connector import Error
import json
import os

# Fetching credentials from env
host = os.getenv('DATABASE_HOST')
db_pass = os.getenv('DATABASE_PW')
db_user = os.getenv('DATABASE_USER')
db = os.getenv('DATABASE')

class ChatDatabase:
    
    # Constructor function to initialize connection parameters
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        
        print("Chat Database Object Initizialized")

    # Method to create a connection
    def create_connection(self):
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

    # Method to create new chat    
    def create_new_chat(self, user_id, chat_id, chat_history):
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

    # Method to update existing chat   
    def update_existing_chat(self, user_id, chat_id, chat_history):
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
    
    # Method to delete chat   
    def delete_chat(self, user_id, chat_id):
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
    
    # Method to check if chat exists    
    def does_chat_exist(self, user_chat_ids) -> bool:
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
    
    # Method to fetch chat history    
    def fetch_chat_data(self, user_chat_ids):
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
