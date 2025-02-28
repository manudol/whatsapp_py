import os
import re
import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import certifi
import ssl

from load_env import load_vars

load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')


def clean_ai_output(ai_output):
    # Remove any header/footer/url annotations from the message body
    pattern = r'(?:OUTPUT TYPE:|HEADER:|FOOTER:|URL:).*?(?:\||$)'
    cleaned_text = re.sub(pattern, '', ai_output).strip()
    return cleaned_text

async def buttonReply(assistant_text, ai_output, phone_number, phone_number_id):
    url = f'https://graph.facebook.com/v21.0/{phone_number_id}/messages'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }
    # Extract header, footer and URL from the assistant_text using the format:
    # OUTPUT TYPE: cta_button | HEADER:header_text | FOOTER:footer_text | URL:url
    pattern = r'HEADER:(.*?)\s*\|\s*FOOTER:(.*?)\s*\|\s*URL:(.*?)(?:\s*$|\s*\|)'
    match = re.search(pattern, assistant_text)
    if match:
        header_text = match.group(1).strip()
        footer_text = match.group(2).strip() 
        button_url = match.group(3).strip()
        button_text = "Click here" # Default button text
        # Clean the ai_output to remove any annotations
        ai_output = clean_ai_output(ai_output)
    else:
        print("No match found in assistant_text:", assistant_text)
        raise ValueError("No match found in assistant_text")

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
                "text": ai_output
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