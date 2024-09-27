import certifi
import aiohttp
import ssl

from openai import OpenAI

from load_env import load_vars
import os


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

async def cta_url(assistant_text, phone_number, phone_number_id):
    client = OpenAI(api_key=OPENAI_API_KEY)
    create_header = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"system": f"{assistant_text}"},
            {"user": ""}
        ]
    )
    HEADER_TEXT = create_header.choices[0].message.content

    create_body = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"system": ""},
            {"user": ""}
        ]
    )
    BODY_TEXT = create_body.choices[0].message.content


    create_footer = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"system": ""},
            {"user": ""}
        ]
    )
    FOOTER_TEXT = create_footer.choices[0].message.content


    create_button_text = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"system": ""},
            {"user": ""}
        ]
    )
    BUTTON_TEXT = create_button_text.choices[0].message.content


    create_button_url = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"system": ""},
            {"user": ""}
        ]
    )
    BUTTON_TEXT = create_button_url.choices[0].message.content

    url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
    headers = {
            'Content-Type: application/json',
           f'Authorization: Bearer {WHATSAPP_TOKEN}'
      }
    
    BUTTON_URL = None

    data = {
                {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": f"{phone_number}",
        "type": "interactive",
        "interactive": {
            "type": "cta_url",
            "header": {
            "type": "text",
            "text": f"{HEADER_TEXT}"
            },
            "body": {
            "text": f"{BODY_TEXT}"
            },
            "footer": {
            "text": f"{FOOTER_TEXT}"
            },
            "action": {
            "name": "cta_url",
            "parameters": {
                "display_text": f"{BUTTON_TEXT}",
                "url": f"{BUTTON_URL}"
            }
            }
        }
        }
    }

    ssl_context = ssl.create_default_context(cafile=certifi.where())

    session = aiohttp.ClientSession()

    async with session.post(url, headers=headers, json=data, ssl_context=ssl_context) as response:
        return await response.json()