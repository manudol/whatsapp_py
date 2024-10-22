import ssl
import aiohttp
import certifi

import os
import re
from openai import OpenAI

from load_env import load_vars


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')



async def emojiReaction(assistant_text, phone_number, phone_number_id, message_id):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=openai_api_key)

    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
        {"role": "system", "content": "Based on the users text choose an appropirate emoji reaction. Only respond with one emoji and no other text. It is vital that you only output one emoji character."},
        {"role": "user", "content": f"{assistant_text}"},
  ]
)
    emoji_reaction = response.choices[0].message.content

    output = ""

    if len(emoji_reaction) == 1:
        output += emoji_reaction
    elif len(emoji_reaction) > 1:
        pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]'
        output += re.findall(pattern, emoji_reaction)

    print("Model reacted with: ", output)
    
    url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
    headers = {
                'Content-Type: application/json', 
               f'Authorization: Bearer {WHATSAPP_TOKEN}'
    }
    data = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": f"{phone_number}",
      "type": "reaction",
      "reaction": {
        "message_id": f"{message_id}",
        "emoji": f"{output}"
      }
    }

    ssl_context = ssl.create_default_context(cafile=certifi.where())

    session = aiohttp.ClientSession()

    async with session.post(url, headers=headers, json=data, ssl_context=ssl_context) as response:
        return await response.json(), await session.close()
  