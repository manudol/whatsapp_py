import aiohttp
import ssl
import certifi
from prompts import craft_genai_prompt
from openai import OpenAI
import json


from load_env import load_vars
from interactObjects.jsonGenAI import GenAIjson
import os


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')


# (WORKS!)
async def buttonReply(assistant_text, phone_number, phone_number_id, user_message, output_type):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    url = f'https://graph.facebook.com/v21.0/{phone_number_id}/messages'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }
    data = craft_genai_prompt(output_type, phone_number)

    gen = GenAIjson(client, data)

    jsonGen = gen.jsonGenAI(assistant_text, user_message)



    print("AI GENERATED JSON DATA: ", jsonGen)

    loaded_json = json.loads(jsonGen)

    ssl_context = ssl.create_default_context(cafile=certifi.where())

    session = aiohttp.ClientSession()

    async with session.post(url, headers=headers, json=loaded_json, ssl_context=ssl_context) as response:
        return await response.json(), await session.close()
    