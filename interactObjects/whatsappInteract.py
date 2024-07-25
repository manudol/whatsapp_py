from load_env import load_vars
import os

import aiohttp
import asyncio
from io import BytesIO
from openai import OpenAI

from responseComponents import card, carousel, markAsRead, text, location, emojiReaction, ctaURL, audioMessage, flows

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

    

    def determine_output_type(self, user_message):
      response = client.chat.completions.create(
          model="gpt-4o-mini",
            messages=[
              {"role": "system", "content": "You are a helpful assistant."},
              {"role": "user", "content": f"{user_message}"}]
      )
      reply = response.choices[0].message.content
      return reply

    

  
    async def send_whatsapp_message(self):
        response = client.chat.completions.create(
          model="gpt-4o-mini",
            messages=[
              {"role": "system", "content": """
                    

                      """
                  },
              {"role": "user", "content": f"{self.assistant_text}"}]
        )
        output_type = response.choices[0].message.content

        output_type_mapping = {
            "text": text(self.assistant_text, self.phone_number, self.phone_number_id),
            "audio": audioMessage(self.assistant_text, self.phone_number, self.phone_number_id),
            "carousel": card(self.assistant_text, self.phone_number, self.phone_number_id),
            "ctaURL": ctaURL(self.assistant_text, self.phone_number, self.phone_number_id),
            # "flow": flows(self.assistant_text, self.phone_number, self.phone_number_id, self.message_id),
            "card": carousel(self.assistant_text, self.phone_number, self.phone_number_id),
            "emoji": emojiReaction(self.assistant_text, self.phone_number, self.phone_number_id, self.message_id),
            "location": location(self.assistant_text, self.phone_number, self.phone_number_id),
            # "markAsRead": markAsRead(self.phone_number_id, self.message_id)
        }

        # Get the corresponding function based on output_type
        post_function = output_type_mapping.get(str(output_type))

        if post_function:
            return await post_function
        else:
            # Default action or error handling
            async with self.session.post("https://api.whatsapp.com/send_default", json=response) as resp:
                return await resp.json()


