import ssl
import aiohttp
import certifi

import os
from openai import OpenAI

from load_env import load_vars


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')

openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)



# (WORKS!)
async def emojiReaction(assistant_text, phone_number, phone_number_id, message_id):
    

    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
        {
          "role": "system", "content": "Based on the users text choose an appropirate emoji\
          reaction. Only respond with one emoji and no other text. It is vital that you only\
          output one emoji character without any spaces."
          },

        {"role": "user", "content": f"{assistant_text}"},
  ]
)
    emoji_reaction = response.choices[0].message.content
    
    
    url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
    headers = {
                'Content-Type': 'application/json', 
               f'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }
    data ={
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": f"{phone_number}",
      "type": "reaction",
      "reaction": {
        "message_id": message_id,
        "emoji": emoji_reaction
      }
    }

    print(data)
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    session = aiohttp.ClientSession()

    async with session.post(url=url, headers=headers, json=data, ssl_context=ssl_context) as response:
        return await response.json(), await session.close()