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
async def audioMessage(assistant_text, phone_number, phone_number_id):
    
    speech_file_path = f"txt2speech_{os.urandom(8).hex()}.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=assistant_text,
    ) as response:
        response.stream_to_file(speech_file_path)

    url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/media'
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
    }
    ctx = ssl.create_default_context(cafile=certifi.where())
    async with httpx.AsyncClient(verify=ctx) as client1:
        with open(speech_file_path, 'rb') as f:
            files = {'file': ('audio.mp3', f, 'audio/mpeg')}
            data = {
                'messaging_product': 'whatsapp',
                'type': 'audio/mpeg'
            }
            
            response = await client.post(url, headers=headers, data=data, files=files)
            response_data = response.json()
            print(response_data)
            audio_id = response_data['id']

            # Send the audio message
            url2 = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
            headers2 = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {WHATSAPP_TOKEN}'
            }
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual", 
                "to": str(phone_number),
                "type": "audio",
                "audio": {
                    "id": str(audio_id)
                }
            }

            os.remove(speech_file_path)

            response = await client1.post(url2, headers=headers2, json=data)
            return response.json()