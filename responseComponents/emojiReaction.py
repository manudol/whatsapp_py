import requests
from openai import OpenAI

from load_env import load_vars
import os


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')



async def emojiReaction(assistant_text, phone_number, phone_number_id, message_id):
    open_ai_api = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=open_ai_api)

    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "Based on the users text choose an appropirate emoji reaction. Only respond with one emoji and no other text. It is vital that you only output one emoji character."},
        {"role": "user", "content": f"{assistant_text}"},
  ]
)
    emoji_reaction = response.choices[0].message.content
    
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
        "emoji": f"{emoji_reaction}"
      }
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()
  