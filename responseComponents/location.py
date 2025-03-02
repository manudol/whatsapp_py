import os
import httpx
import certifi
import ssl

from load_env import load_vars

from interactObjects.djangoInteract import Getters

load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')


# (WORKS!)
async def location(assistant_text, ai_output, phone_number, phone_number_id, access_token, business_id):
    getters = Getters(access_token, business_id)
    latitude, longitude, name, address = getters.get_location(ai_output)


    url = f'https://graph.facebook.com/v21.0/{phone_number_id}/messages'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }
    
    
    
    body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual", 
        "to": phone_number,
        "type": "location",
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "name": name,
            "address": address
        }
    }
    ctx = ssl.create_default_context(cafile=certifi.where())

    async with httpx.AsyncClient(verify=ctx) as client:
        response = await client.post(url, headers=headers, json=body)
        return response.json()