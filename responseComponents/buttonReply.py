import os
import httpx
import certifi
import ssl

from pydantic import BaseModel

from load_env import load_vars
from interactObjects.structo import Structo

from interactObjects.djangoInteract import Getters

load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')




async def buttonReply(assistant_text, ai_output, phone_number, phone_number_id, access_token, business_id):
    getters = Getters(access_token, business_id)
    header_text, body_text, footer_text, button_text, button_url = getters.get_cta_url(ai_output)

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

                "header": {
                "type": "text",
                "text": header_text
                },

                "body": {
                "text": body_text
                },
                "footer": {
                "text": footer_text
                },
                "action": {
                "name": "cta_url",
                "parameters": {
                    "display_text": button_text,
                    "url": button_url
                    }
                }
            }
        }

    ctx = ssl.create_default_context(cafile=certifi.where())
    async with httpx.AsyncClient(verify=ctx) as client:
        response = await client.post(url, headers=headers, json=json_body)
        return response.json()