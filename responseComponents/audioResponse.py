import aiohttp
import ssl
import certifi

from openai import OpenAI

from load_env import load_vars
import os


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')


# (WORKS!)
async def audioMessage(assistant_text, phone_number, phone_number_id):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)
    
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
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession() as session:
        with open(speech_file_path, 'rb') as f:
            
            form_data = aiohttp.FormData()
            form_data.add_field('messaging_product', 'whatsapp')
            form_data.add_field('type', 'audio/mpeg')
            form_data.add_field('file', f, filename=speech_file_path, content_type='audio/mpeg')
            
            async with session.post(url, headers=headers, data=form_data, ssl_context=ssl_context) as response:
                response_data = await response.json()
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
                    "to": f"{phone_number}",
                    "type": "audio",
                    "audio": {
                        "id": f"{audio_id}"
                        }
                }

                os.remove(speech_file_path)

                async with session.post(url2, headers=headers2, json=data, ssl_context=ssl_context) as response1:
                    return await response1.json(), await session.close()