import os
import json
from .interact import Interact
from openai import OpenAI
from load_env import load_vars
from prompts import craft_genai_prompt

load_vars()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)



# Json Gen AI generates json body for api requests


class GenAIjson():

    def __init__(self, client, data):
        self.client = client
        self.data_type = data
        self.get_assisstant()


    def get_assisstant(self):
        
        assistant_file_path = "assistant.json"

        if os.path.exists(assistant_file_path):
            with open(assistant_file_path, "r") as file:
                assistant_data = json.load(file)
                assistant_id = assistant_data.get('assistant_id')
        else:
            assistant = client.beta.assistants.create(
                instructions="You are a json generative ai assistant you are made to geneerate\
                        content that is used to create interactive response componenets in whatsapp\
                        follow the json generation method\
                        this is job where you need to follow the instruction exactly.\
                        to generate proper json bodies for api calls.\
                        NEVER EVER surround the json body by ```json {json body} ``` triple quotes. It should just be: {json body}",
                model="gpt-4o-mini",
                )

            assistant_id = assistant.id
            with open(assistant_file_path, 'w') as file:
                json.dump({'assistant_id': assistant.id}, file)

        thread = client.beta.threads.create()
        thread_id = thread.id

        return {"assistant_id": assistant_id, "thread_id": thread_id}



    def jsonGenAI(self, assistant_text, user_message):
        data = self.get_assisstant()
        assistant_id = data["assistant_id"]
        thread_id = data["thread_id"]
        
        client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=f"Data structure to generate {self.data_type},\
                        decide by the messaging ai assistant in: {assistant_text}.\
                            in response to: {user_message}"
                )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
                
        
        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread_id,)
            message_content = messages.data[0].content[0].text
            # Remove annotations
            annotations = message_content.annotations
            for annotation in enumerate(annotations):
                message_content.value = message_content.value.replace(annotation.text, '')
            print("Run completed, returning response")
            print("Response:", message_content.value)
            response = message_content.value

            return response