import requests

from load_env import load_vars
import os


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')


async def send_location(assistant_text, phone_number, phone_number_id):
  location_payload = None  # fetch the paylaod from the assistant_text


  url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
  headers = {
            'Content-Type: application/json',
           f'Authorization: Bearer {WHATSAPP_TOKEN}'
      }
  data = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": f"{phone_number}",
      "type": "location",
      "location": {
          "latitude": location_payload['latitude'],
          "longitude": location_payload['longitude'],
          "name": location_payload['name'],
          "address": location_payload['address'],
      }
  }
  response = requests.post(url, headers=headers, data=data)
  return response.json()