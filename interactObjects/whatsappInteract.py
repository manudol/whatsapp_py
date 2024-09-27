from load_env import load_vars
import os
import re

import certifi
import ssl
import aiohttp
import asyncio
from io import BytesIO
from openai import OpenAI

from responseComponents import audioResponse, card, carousel, text, emojiReaction, ctaURL

load_vars()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_VERSION = os.getenv("WHATSAPP_VERSION")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")


client = OpenAI(api_key=OPENAI_API_KEY)


class WhatsAppHandler:

    def __init__(self, assistant_text, WHATSAPP_TOKEN, WHATSAPP_VERSION, phone_number_id, user_name, client, phone_number, message_id):
        self.session = aiohttp.ClientSession()
        self.WHATSAPP_TOKEN = WHATSAPP_TOKEN
        self.WHATSAPP_VERSION = WHATSAPP_VERSION
        self.phone_number_id = phone_number_id
        self.client = client
        self.user_name = user_name
        self.phone_number = phone_number
        self.assistant_text = assistant_text
        self.message_id = message_id
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                ssl=ssl.create_default_context(cafile=certifi.where())
            )
        )

    
    async def close_session(self):
        await self.session.close()
  
    async def send_whatsapp_message(self):
        print(self.assistant_text)
        # Define the regular expression pattern to find the end message
        pattern = r'\s*OUTPUT TYPE:\s*\'([^\']+)\'$'
        
        # Search for the pattern in the text
        match = re.search(pattern, str(self.assistant_text), re.IGNORECASE)
        
        # If a match is found, extract the output type and remove it from the text
        if match:
            output_type = match.group(1).lower()  # Extract and lowercase the output type
            ai_output = re.sub(pattern, '', str(self.assistant_text), flags=re.IGNORECASE)  # Remove the pattern from the text
            print("New reformatted text: ", ai_output)
            print(output_type)
            output_type_mapping = {
                "text": text.text,
                "audio": audioResponse.audioMessage,
                "carousel": carousel.carousel,
                "ctaURL": ctaURL.cta_url,
                # "flow": flows,
                "card": card.card,
                "emoji_react": emojiReaction.emojiReaction,
                # "location": location.send_location,
                # "markAsRead": markAsRead
            }

            # Get the corresponding function based on output_type
            post_function = output_type_mapping.get(str(output_type))

            args_mapping = {
                "text": (ai_output, self.phone_number, self.phone_number_id),
                "audio": (ai_output, self.phone_number, self.phone_number_id),
                "carousel": (ai_output, self.phone_number, self.phone_number_id),
                "ctaURL": (ai_output, self.phone_number, self.phone_number_id),
                # "flow": flows,
                "card": (ai_output, self.phone_number, self.phone_number_id),
                "emoji_react": (ai_output, self.phone_number, self.phone_number_id, self.message_id),
                # "location": (ai_output, self.phone_number, self.phone_number_id),
                # "markAsRead": markAsRead
            }

            args = args_mapping.get(str(output_type))

            if post_function:
                print(f"Trigerring function: {post_function.__name__}")
                return await post_function(*args)
            else:
                # Default action or error handling
                response = {"message": "no message"}
                async with self.session.post(url="https://api.whatsapp.com/send_default", json=response) as resp:
                    return await resp.json()
                
        else:
            # Default action or error handling
            response = {"message": "no message"}
            async with self.session.post(url="https://api.whatsapp.com/send_default", json=response) as resp:
                return await resp.json()


