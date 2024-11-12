import os
from load_env import load_vars

import psycopg2

load_vars()

class DatabaseManager:
    def __init__(self, phone_number, phone_number_id):
        self.phone_number = phone_number
        self.phone_number_id = phone_number_id
        self.conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
        )
        self.cursor = self.conn.cursor()
    


    def check_if_thread_exists(self):
        query = "SELECT thread_id FROM threads WHERE phone_number = %s;"
        self.cursor.execute(query, (self.phone_number,))
        result = self.cursor.fetchone()
        return result[0] if result else None



    def store_thread(self, thread_id):
        query = """
        INSERT INTO threads (phone_number, thread_id)
        VALUES (%s, %s)
        ON CONFLICT (phone_number) DO UPDATE
        SET thread_id = EXCLUDED.thread_id;
        """
        self.cursor.execute(query, (self.phone_number, thread_id))
        self.conn.commit()



    def check_if_assistant_exists(self):
        query = "SELECT assistant_id FROM assistants WHERE phone_number = %s;"
        self.cursor.execute(query, (self.phone_number,))
        result = self.cursor.fetchone()
        return result[0] if result else None



    def store_assistant(self, assistant_id):
        query = """
        INSERT INTO assistants (phone_number, assistant_id)
        VALUES (%s, %s)
        ON CONFLICT (phone_number) DO UPDATE
        SET assistant_id = EXCLUDED.assistant_id;
        """
        self.cursor.execute(query, (self.phone_number, assistant_id))
        self.conn.commit()



    def close(self):
        self.cursor.close()
        self.conn.close()
