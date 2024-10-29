import os
import ssl
import certifi

import aiohttp

from load_env import load_vars



load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')


async def sendLocation(assistant_text, phone_number, phone_number_id):
    url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }
    
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "interactive",
        "to": phone_number,
        "interactive": {
            "type": "location_request_message",
            "body": {
            "text": assistant_text
            },
            "action": {
            "name": "send_location"
            }
        }
    }
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    session = aiohttp.ClientSession()

    async with session.post(url, headers=headers, json=data, ssl_context=ssl_context) as response:
        return await response.json(), await session.close()