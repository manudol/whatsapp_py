import os
import time
import json
import requests
import shelve
import asyncio

from openai import OpenAI
from prompts import system_prompt

from load_env import load_vars

load_vars()

openai_api_key = os.getenv("OPENAI_API_KEY")
# airtable_api_key = os.getenv("AIRTABLE_API_KEY")


client = OpenAI(api_key=openai_api_key)
        

# Interact class to manage interactions
class Interact:

    def __init__(self, phone_number, phone_number_id, client, WHATSAPP_VERSION, WHATSAPP_TOKEN, user_name):
        self.phone_number_id = phone_number_id
        self.client = client
        self.user_name = user_name
        self.phone_number = phone_number
        # self.airtable_api_key = airtable_api_key
        self.WHATSAPP_VERSION = WHATSAPP_VERSION
        self.WHATSAPP_TOKEN = WHATSAPP_TOKEN
        # self.assistant_id = None
        # self.thread_id = None
        self.initialize_assistant()

    
    def initialize_assistant(self):
        thread_id = self.check_if_thread_exists()
        assistant_id = self.check_if_assistant_exists()
        if assistant_id and thread_id is None:
            assistant_id = self.create_assistant()
            thread_id = self.create_thread()
            self.store_thread(thread_id)
            self.store_assistant(assistant_id)
            print(f"Creating thread and assistant for new user: {self.user_name}, with phone number {self.phone_number}")
        
        # Otherwise, retrieve the existing thread
        else:
            print(f"Retrieving existing thread & assistant for {self.user_name} with phone number {self.phone_number}")
        
        return {"assistant_id": assistant_id, "thread_id": thread_id}
            

        
    # Thread management

    def check_if_thread_exists(self):
        with shelve.open("threads_db") as threads_shelf:
            return threads_shelf.get(self.phone_number, None)


    def store_thread(self, thread_id):
        with shelve.open("threads_db", writeback=True) as threads_shelf:
            threads_shelf[self.phone_number] = thread_id

    
    # Assistant management

    def check_if_assistant_exists(self):
        with shelve.open("assistants_db") as assistants_shelf:
            return assistants_shelf.get(self.phone_number, None)


    def store_assistant(self, assistant_id):
        with shelve.open("assistants_db", writeback=True) as assistants_shelf:
            assistants_shelf[self.phone_number] = assistant_id




    def create_assistant(self):
        # Create a vector store caled "Financial Statements"
        vector_store = client.beta.vector_stores.create(name="Farmapiel Vector Store")

        # Ready the files for upload to OpenAI 
        file_paths = ["./databases/farmapiel_shipping_return_policy.docx", 
                    "./databases/farmapiel_privacy_policy.docx", 
                    "./databases/farmapiel_terms_of_service.docx", 
                    "./databases/Help Center Farmapiel - Digital Farmapiel.pdf", 
                    "./databases/farmapiel_product_list.docx"]
        file_streams = [open(path, "rb") for path in file_paths]

        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
        )

        # You can print the status and the file counts of the batch to see the result of this operation. 
        print(file_batch.status)
        print(file_batch.file_counts)

    # Then reference the collected file IDs
        assistant = client.beta.assistants.create(
            instructions=system_prompt,
            model="gpt-4o",
            tools=[
                {
                    "type": "file_search"
                },
            ],
            tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store.id]
            }
            })

        assistant_id = assistant.id

        return assistant_id



    def create_thread(self):
        thread = client.beta.threads.create()
        print("Thread_ID created successfully: ", thread.id)
        return thread.id
  
    
    
    
    async def interact_w_ass1(self, payload):
        message_type = payload["type"]
        user_message = payload["text"]
        result = self.initialize_assistant()
        if "assistant_id" in result:
            assistant_id = result["assistant_id"]
            thread_id = result["thread_id"]
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=f"Information about the message from the user: {message_type}, And the actual user_message: {user_message}"
            )

            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            run_id = run.id
            
            start_time = time.time()
            while time.time() - start_time < 30:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run_id
                )
                print("Checking run status:", run_status.status)
        
                if run_status.status == 'completed':
                    messages = client.beta.threads.messages.list(thread_id=thread_id)
                    message_content = messages.data[0].content[0].text
                    # Remove annotations
                    annotations = message_content.annotations
                    for annotation in annotations:
                        message_content.value = message_content.value.replace(annotation.text, '')
                    print("Run completed, returning response")
                    print("Response:", message_content.value)
                    response = message_content.value
        
                    return {"response": response, "status": "completed"}
                else:
                    await asyncio.sleep(1)  # Add a small delay to avoid spamming the API
            else:
                print("Run not completed in time, restarting function")
                return 400


    
    
            
            




"""
# Example usage
phone_number = "123-456-7890"
interaction = Interact(phone_number)
print(f"Assistant ID: {interaction.assistant_id}")
print(f"Thread ID: {interaction.thread_id}")
"""