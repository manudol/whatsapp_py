import aiohttp
import ssl
import certifi


import requests
import tempfile
from openai import OpenAI

from load_env import load_vars
import os


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')



async def audioMessage(assistant_text, phone_number, phone_number_id):
    client = OpenAI(api_key=OPENAI_API_KEY)
    audio = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=assistant_text,
    )

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio_file:
        temp_audio_file.write(audio['data'])
        temp_audio_path = temp_audio_file.name

    # URLs and headers for requests
    url1 = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/media'
    headers1 = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }
    url2 = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
    headers2 = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }

    files = {
        'file': open(temp_audio_path, 'rb'),
        'type': 'audio/mpeg',
        'messaging_product': 'whatsapp'
    }

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": f"{phone_number}",
        "type": "audio",
    }

    async with aiohttp.ClientSession() as session:
        # Upload the audio file to WhatsApp
        async with session.post(url1, headers=headers1, json=files) as wa_file_upload:
            wa_file_upload_json = await wa_file_upload.json()
            audio_id = wa_file_upload_json.get('id')

            # Send the audio message
            data["audio"] = {"id": audio_id}
            async with session.post(url2, headers=headers2, json=data) as response:
                return await response.json()