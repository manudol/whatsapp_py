import requests

from load_env import load_vars
import os


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')

async def markAsRead(phone_number_id, message_id):
  url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
  headers = {
            f'Authorization: Bearer {WHATSAPP_TOKEN}'
            'Content-Type: application/json'
      }

  data = {
  "messaging_product": "whatsapp",
  "status": "read",
  "message_id": f"{message_id}"
  }
  response = requests.post(url, headers=headers, data=data)
  return response.json()


"""
Example Response:

  {
    "success": true
  }
"""