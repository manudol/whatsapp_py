import os
import certifi
import httpx
import ssl

from pydantic import BaseModel

from load_env import load_vars

from interactObjects.structo import Structo

load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')

# (WORKS!)
async def text(output_type, assistant_text, phone_number, phone_number_id):
    
    class Text(BaseModel):
        text: str

    structo = Structo(assistant_text, Text)
    structo_response = structo.get_structo()

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
        "body": f"{structo_response.text}"
      }
    }
    ctx = ssl.create_default_context(cafile=certifi.where())

    async with httpx.AsyncClient(verify=ctx) as client:
        response = await client.post(url, headers=headers, json=data)
        return await response.json(), await client.aclose()