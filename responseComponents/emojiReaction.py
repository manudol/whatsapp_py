import os
import httpx
import certifi
import ssl

from openai_client.client import client

from load_env import load_vars

load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')

# (WORKS!)
async def emojiReaction(assistant_text, phone_number, phone_number_id, message_id):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "system", 
                "content": "Based on the users text choose an appropirate emoji\
                reaction. Only respond with one emoji and no other text. It is vital that you only\
                output one emoji character without any spaces."
            },
            {"role": "user", "content": f"{assistant_text}"},
        ]
    )
    emoji_reaction = response.choices[0].message.content
    
    url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual", 
        "to": str(phone_number),
        "type": "reaction",
        "reaction": {
            "message_id": message_id,
            "emoji": emoji_reaction
        }
    }
    ctx = ssl.create_default_context(cafile=certifi.where())
    async with httpx.AsyncClient(verify=ctx) as client1:
        response = await client1.post(url, headers=headers, json=data)
        return await response.json(), await client1.aclose()