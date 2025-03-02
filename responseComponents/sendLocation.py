import os
import httpx
import certifi
import ssl

from pydantic import BaseModel

from load_env import load_vars

from interactObjects.structo import Structo

load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')


async def sendLocation(assistant_text, phone_number, phone_number_id):

    class LocationRequest(BaseModel):
        text: str

    structo = Structo(assistant_text, LocationRequest)
    structo_response = structo.get_structo()

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
                "text": structo_response.text
            },
            "action": {
                "name": "send_location"
            }
        }
    }
    ctx = ssl.create_default_context(cafile=certifi.where())

    async with httpx.AsyncClient(verify=ctx) as client:
        response = await client.post(url, headers=headers, json=data)
        return await response.json(), await client.aclose()