import os
import json

from load_env import load_vars

from .rag import GetMessages
from outputs_instruct import Prompts

load_vars()

from openai_client.client import client

# Interact class to manage interactions
class Interact:
    def __init__(self, phone_number, phone_number_id, model_id, 
                 user_name, access_token, system_prompt, thread_id):
        
        self.phone_number_id = phone_number_id
        self.model_id = model_id
        self.system_prompt = system_prompt
        self.access_token = access_token
        self.user_name = user_name
        self.phone_number = phone_number
        self.thread_id = thread_id
        self.file_path = "./threads/" + self.thread_id + ".json"
        self.check_thread_file()


    def check_thread_file(self):
        thread = {}
        # Try to open and read the file
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                thread = json.load(f)
                if thread:
                    return self.thread_id
        else:
            thread["id"] = self.thread_id
            thread['messages'] = []
            self.json_write(thread)
    
        return thread['id']
    

    def json_write(self, data):
        with open(self.file_path, 'w') as f: json.dump(data, f)


    def json_get(self):
        with open(self.file_path, 'r') as f: 
            conversation = json.load(f) 
            return conversation

    
    def messageAI(self, payload):
        message_type = payload["type"]
        user_message = payload["text"]

        past_messages = GetMessages(self.file_path).get_json()

        conversation = self.json_get()
        conversation['messages'].append({"role": "user",
                                         "content": str(user_message)})

        output_instructions = Prompts.Whatsapp.whatsapp_prompt
        completion = client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": f"Context from 20 past messages or less: {past_messages}. \
                                                User Message Type: {message_type}. \
                                                Instructions: {self.system_prompt} \
                                                Output Instructions: {output_instructions}"},

                {"role": "user", "content": f"{user_message}"}
            ]
        )

        conversation['messages'].append({"role": "assistant",
                                         "content": completion.choices[0].message.content})

        self.json_write(conversation)
        
        return completion.choices[0].message.content