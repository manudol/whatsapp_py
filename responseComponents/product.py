import os
import httpx
import certifi
import ssl

from load_env import load_vars

from interactObjects.djangoInteract import Getters

load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')
BACKEND_URL = os.getenv('BACKEND_URL')




# (WORKS!)
async def product(ai_output, phone_number, phone_number_id, access_token, business_id):
    getters = Getters(access_token, business_id)
    
    image_url, button_text, button_url = getters.get_product(ai_output)

    url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": f"{phone_number}",
        "type": "image",
        "image": {
            "link": image_url,
            "caption": ""
            }
        }
    ctx = ssl.create_default_context(cafile=certifi.where())
    async with httpx.AsyncClient(verify=ctx) as client2:
        response = await client2.post(url, headers=headers, json=data)
        res, _ = await response.json(), await client2.aclose()
        
        if len(res['messages']) > 0:
            url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {WHATSAPP_TOKEN}'
            }
            json_body = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": str(phone_number),
                    "type": "interactive",
                    "interactive": {
                        "type": "cta_url",
                        "action": {
                        "name": "cta_url",
                        "parameters": {
                            "display_text": button_text,
                            "url": button_url
                            }
                        }
                    }
                }
            ctx1 = ssl.create_default_context(cafile=certifi.where())
            async with httpx.AsyncClient(verify=ctx1) as client3:
                response1 = await client3.post(url, headers=headers, json=json_body)
                return await response1.json(), await client3.aclose()

