import os
import time
import shelve

from openai import OpenAI

from prompts import system_prompt
from .databaseManager import DatabaseManager
from load_env import load_vars

load_vars()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)
        

# Interact class to manage interactions
class Interact(DatabaseManager):

    def __init__(self, phone_number, phone_number_id, client, user_name):
        super().__init__(phone_number, phone_number_id)
        self.phone_number_id = phone_number_id
        self.client = client
        self.user_name = user_name
        self.phone_number = phone_number
        self.initialize_assistant()


    
    def initialize_assistant(self):
        thread_id = self.check_if_thread_exists()
        assistant_id = self.check_if_assistant_exists()
    
        if assistant_id == None and thread_id == None:
            print("No threads or assistant detected. Creating them now...")
            assistant_id = self.create_assistant()
            thread_id = self.create_thread()
            self.store_thread(thread_id)
            self.store_assistant(assistant_id)
            print("Creating Thread_id: ", thread_id)
            print("Creating Assistant_id: ", assistant_id)
            print(f"Creating thread and assistant for new user: {self.user_name}, with phone number {self.phone_number}")
        
        # Otherwise, retrieve the existing thread
        else:
            print(f"Retrieving existing thread {thread_id} & assistant {assistant_id} for {self.user_name} with phone number {self.phone_number}")
        
        return {"assistant_id": assistant_id, "thread_id": thread_id}



    def create_assistant(self):
    # Then reference the collected file IDs
        assistant = client.beta.assistants.create(
            instructions=system_prompt,
            model="gpt-4o-mini",
            )

        assistant_id = assistant.id

        return assistant_id



    def create_thread(self):
        thread = client.beta.threads.create()
        print("Thread_ID created successfully: ", thread.id)
        return thread.id
  
    
    
    
    def messageAI(self, payload):
        message_type = payload["type"]
        user_message = payload["text"]
        result = self.initialize_assistant()
        if "assistant_id" in result:
            assistant_id = result["assistant_id"]
            thread_id = result["thread_id"]

            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=f"Information on user_message: {message_type}, user_message: {user_message}"
            )

            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            
    
            if run.status == 'completed':
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                message_content = messages.data[0].content[0].text
                # Remove annotations
                annotations = message_content.annotations
                for annotation in enumerate(annotations):
                    message_content.value = message_content.value.replace(annotation.text, '')
                print("Run completed, returning response")
                print("Response:", message_content.value)
                response = message_content.value

                return response
            
            else:
                time.sleep(1)  # Add a small delay to avoid spamming the API
        else:
            print("Run not completed in time, restarting function")
            return 400
        

        