import requests

from load_env import load_vars
import os


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')


async def text(assistant_text, phone_number, phone_number_id):
    url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
    headers = {
              'Content-Type: application/json',
              f'Authorization: Bearer {WHATSAPP_TOKEN}'
  }
    data = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": f"{phone_number}",
      "type": "text",
      "text": {
        "preview_url": True,
        "body": f"{assistant_text}"
      }
    }
    
    response = requests.post(url, headers=headers, data=data)
    return response.json()






"""
# Example Response:

{
  "messaging_product": "whatsapp",
  "contacts": [
    {
      "input": "+16505551234",
      "wa_id": "16505551234"
    }
  ],
  "messages": [
    {
      "id": "wamid.HBgLMTY0NjcwNDM1OTUVAgARGBI1RjQyNUE3NEYxMzAzMzQ5MkEA"
    }
  ]
}
"""