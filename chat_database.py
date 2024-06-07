import mysql.connector
from mysql.connector import Error
import json

class ChatDatabase():
    
    # Constructer function with parameters to initialize connection
    def __init__(self, host, user, password, database):
        
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        
        # Making connection with the database
        try:
            self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
            )
            
            if self.connection.is_connected():
                print("Successfully connected to the database")
                
        except Error as e:
            print(f"Error: {e}")
            
        
    def create_new_chat(self, user_id, chat_id, chat_history):
        
        insert_query = """
        INSERT INTO chats (user_id, chat_id, chat_history)
        VALUES (%s, %s, %s)
        """
        
        # Create a cursor object
        cursor = self.connection.cursor()
        
        # Define dictionary for chat history to convert it into JSON
        chat_dict = {
            'chat_history' : chat_history
        }
        
        # Convert the dictionary to a JSON string
        chat_history_json = json.dumps(chat_dict)
        
        # Create tuple for values
        values = (user_id, chat_id, chat_history_json)
        
        # Execute SQL insert chat query
        cursor.execute(insert_query, values)
        
        # Commit the transaction
        self.connection.commit()
        
        
    def update_existing_chat(self, user_id, chat_id, chat_history):
        
        update_query = """
        UPDATE chats
        SET chat_history = %s
        WHERE user_id = %s AND chat_id= %s
        """
        
        # Create a cursor object
        cursor = self.connection.cursor()
        
        # Define dictionary for chat history to convert it into JSON
        chat_dict = {
            'chat_history' : chat_history
        }
        
        # Convert the dictionary to a JSON string
        chat_history_json = json.dumps(chat_dict)
        
        # Create tuple for values
        values = (chat_history_json, user_id, chat_id)
        
        # Execute SQL insert chat query
        cursor.execute(update_query, values)
        
        # Commit the transaction
        self.connection.commit()
        
    def delete_chat(self, user_id, chat_id):
        
        delete_query = """
        DELETE FROM chats
        WHERE user_id = %s AND chat_id= %s
        """
        
        # Create a cursor object
        cursor = self.connection.cursor()

        # Create tuple for values
        values = (user_id, chat_id)
        
        # Execute SQL insert chat query
        cursor.execute(delete_query, values)
        
        # Commit the transaction
        self.connection.commit()
        
    def does_chat_exist(self, user_chat_ids) -> bool:
        
        fetch_query = """
            SELECT chat_history
            FROM chats
            WHERE user_id = %s AND chat_id = %s
        """
        
        # Create a cursor object
        cursor = self.connection.cursor()
        
        values = (user_chat_ids['user_id'], user_chat_ids['chat_id'])
        
        cursor.execute(fetch_query, values)
        
        if(cursor.fetchone()):
            return True
        else:
            return False
        
        
    def fetch_chat_data(self, user_chat_ids):
        
        fetch_query = """
            SELECT chat_history
            FROM chats
            WHERE user_id = %s AND chat_id = %s
        """
        
        # Create a cursor object
        cursor = self.connection.cursor()
        
        values = (user_chat_ids['user_id'], user_chat_ids['chat_id'])
        
        cursor.execute(fetch_query, values)
        
        chat = cursor.fetchone()
        
        if(chat):
            # Get JSON Object of chat history
            chat_json = chat[0]
            
             # Convert the JSON string to a Python dictionary          
            chat_dict = json.loads(chat_json)
            
            return chat_dict['chat_history']
        
        else:
            return []
            
if __name__ == "__main__":       
        
    chat = ChatDatabase(
        'chatbot-user-chats-data.c32iyywau6nz.ap-south-1.rds.amazonaws.com',
        'admin',
        'alihamza123',
        'chat_history'
    )



