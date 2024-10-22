import ssl
import aiohttp
import certifi

from load_env import load_vars
import os


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

async def card(assistant_text, phone_number, phone_number_id):
    cta_url = None
    image_url = None

    url1 = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/media'
    headers1 = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }
    files = {
        'file': f'{image_url}',
        'type': 'image/png',
        'messaging_product': 'whatsapp'
    }

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(
            ssl=ssl.create_default_context(cafile=certifi.where())
        )
    ) as session:
        async with session.post(url1, headers=headers1, json=files) as wa_file_upload:
            wa_file_upload_json = await wa_file_upload.json()

        image_id = wa_file_upload_json.get('id')

        url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {WHATSAPP_TOKEN}'
        }
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": f"{phone_number}",
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "image",
                    "image": {
                        "id": f"{image_id}"
                    }
                },
                "body": {
                    "text": f"{assistant_text}"
                },
                "action": {
                    "name": "cta_url",
                    "parameters": {
                        "display_text": "Check Out Now",
                        "url": f"{cta_url}"
                    }
                }
            }
        }

        async with session.post(url, headers=headers, json=data) as response:
            return await response.json(), await session.close()