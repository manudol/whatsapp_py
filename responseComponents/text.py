import aiohttp
import ssl
import certifi
import asyncio

from load_env import load_vars
import os


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')


async def text(assistant_text, phone_number, phone_number_id):
    url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
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
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    session = aiohttp.ClientSession()

    async with session.post(url, headers=headers, json=data, ssl_context=ssl_context) as response:
        return await response.json()





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