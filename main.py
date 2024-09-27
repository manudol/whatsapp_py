from load_env import load_vars
from save_img import execute_download
import tracemalloc

import json
import os
import requests
from flask import Flask, jsonify, request, make_response
from openai import OpenAI
import asyncio
import certifi
import aiohttp
from aiohttp import web
import ssl
from threading import Lock

# session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl_context=certifi.where()))

from interactObjects.interact import Interact
from interactObjects.processDocs import ProcessDocs
from interactObjects.whatsappInteract import WhatsAppHandler

# app = Flask(__name__)

load_vars()

execute_download()

processing_lock = Lock()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_VERSION = os.getenv("WHATSAPP_VERSION")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)




async def get_verify(request):
    mode = request.query.get('hub.mode')
    token = request.query.get('hub.verify_token')
    challenge = request.query.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == 'whatsapp_co123':
            return web.Response(text=challenge)
        else:
            return web.Response(status=403)
    else:
        return web.Response(status=400)
    



async def webhook(request):
    body = await request.json()
    object = body.get('object')
    if object:
        # IF MESSAGE DOES NOT COME FROM BUTTON
        is_not_interactive = body.get('entry', [])[0].get('changes', [])[0].get('value', {}).get('messages', [])

        if is_not_interactive:

            # WHATSAPP BUSINESS PHONE NUMBER ID for the url Endpoint
            phone_number_id = body['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']

            print("Phone Number ID: ", phone_number_id)


            # Customer's phone number:
            phone_number = body['entry'][0]['changes'][0]['value']['messages'][0]['from']


            # Customer's Whastapp User Name :
            user_name = body['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
            
            message_id = body['entry'][0]['changes'][0]['value']['messages'][0]['id']
            print('Message ID: ', message_id)
            
            #FOR TEXT
            if body['entry'][0]['changes'][0]['value']['messages'][0].get('text'):
                 
               user_message = body['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']


               interact = Interact(phone_number, phone_number_id, client, WHATSAPP_VERSION, WHATSAPP_TOKEN, user_name)


               assistant_response = interact.interact_w_ass1(payload={
                    "type": "text",
                    "text": user_message
               })
               

               print("Assistant Response: ", assistant_response)

               whatsapp = WhatsAppHandler(assistant_response, WHATSAPP_TOKEN, WHATSAPP_VERSION, phone_number_id, user_name, client, phone_number, message_id)
               
               # Acquire lock to ensure single processing
               if processing_lock.acquire(blocking=False):
                    try:
                        await whatsapp.send_whatsapp_message()
                    except Exception as e:
                        return web.json_response({"status": "error", "message": str(e)}, status=500)
                    finally:
                        processing_lock.release()
                        await whatsapp.close_session()
               else:
                    return web.json_response({"status": "already processing"}, status=202)



            #FOR AUDIO
            elif body['entry'][0]['changes'][0]['value']['messages'][0].get('audio'):
                if body['entry'][0]['changes'][0]['value']['messages'][0]['audio'].get('voice'):
                    media_url_response = requests.get(
                        f"https://graph.facebook.com/{WHATSAPP_VERSION}/{body['entry'][0]['changes'][0]['value']['messages'][0]['audio']['id']}",
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {WHATSAPP_TOKEN}',
                        }
                    )
                    media_url = media_url_response.json()['url']

                    rnd_file_name = f"audio_{os.urandom(8).hex()}.ogg"
                    audio_response = requests.get(media_url, headers={'Authorization': f'Bearer {WHATSAPP_TOKEN}'}, stream=True)

                    with open(rnd_file_name, 'wb') as f:
                        for chunk in audio_response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    # Assuming openai is set up correctly
                    
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=open(rnd_file_name, 'rb')
                    )
                    audio_transcript = transcription.text

                    interact = Interact(phone_number, phone_number_id, client, WHATSAPP_VERSION, WHATSAPP_TOKEN, user_name)

                    
                    if audio_transcript:
                        assistant_response = interact.interact_w_ass1(
                            payload={
                                'type': 'audio',
                                'payload': audio_transcript,
                            }
                        )
                        
                        whatsapp = WhatsAppHandler(assistant_response, WHATSAPP_TOKEN, WHATSAPP_VERSION, phone_number_id, user_name, client, phone_number, message_id)

                        response = await whatsapp.send_whatsapp_message()
                        await whatsapp.close_session()
                        return web.json_response({"response": f"{response}","status": "success"})

            # FOR IMAGE
            elif body['entry'][0]['changes'][0]['value']['messages'][0].get('image'):
                if body['entry'][0]['changes'][0]['value']['messages'][0]['type'] == 'image':
                    try:
                        media_response = requests.get(
                            f"https://graph.facebook.com/{WHATSAPP_VERSION}/{body['entry'][0]['changes'][0]['value']['messages'][0]['image']['id']}",
                            headers={
                                'Content-Type': 'application/json',
                                'Authorization': f'Bearer {WHATSAPP_TOKEN}',
                            }
                        )
                        gpt_image_url = media_response.json()['url']


                        interact = Interact(phone_number, phone_number_id, client, WHATSAPP_VERSION, WHATSAPP_TOKEN, user_name)

                        whatsapp = WhatsAppHandler(assistant_response, WHATSAPP_TOKEN, WHATSAPP_VERSION, phone_number_id, user_name, client, phone_number, message_id)
                        

                        image_vision = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Give a clear description of the image that you see. Start your answer by: '{This is the image that the customer sent.}. Including the brackets please.'"
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": gpt_image_url}
                                    }
                                                ]
                                            }
                                        ]
                                    )
                        image_transcript = image_vision.choices[0].message.content

                        if image_transcript:
                            assistant_response = interact.interact_w_ass1(
                                payload={
                                    'type': 'image',
                                    'content': image_transcript,
                                }
                            )
                            response = await whatsapp.send_whatsapp_message()
                            await whatsapp.close_session()
                            return web.json_response({"response": f"{response}","status": "success"})
                        
                    except Exception as e:
                        print(f"Error fetching media URL: {e}")
                        return web.json_response({"status": "error", "message": str(e)}, status=500)


            
            # FOR DOCUMENTS
            elif body['entry'][0]['changes'][0]['value']['messages'][0].get('document'):
                document_info = body['entry'][0]['changes'][0]['value']['messages'][0].get('document')
                if document_info:
                    document_id = document_info['id']
                    mime_type = document_info['mime_type']
                    filename = document_info['filename']
                    # Step 2: Download the document
                    document_url = f"https://graph.facebook.com/{WHATSAPP_VERSION}/{document_id}"
                    headers = {
                        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
                    }
                    response = requests.get(document_url, headers=headers)
                    if response.status_code == 200:
                        with open(filename, 'wb') as file:
                            file.write(response.content)
                        print(f"Document {filename} downloaded successfully.")

                    # Step 3: Process the document
                        doc_process = ProcessDocs(filename, mime_type)
                        file_content = doc_process.process_document(filename, mime_type)
                        
                        interact = Interact(phone_number, phone_number_id, client, WHATSAPP_VERSION, WHATSAPP_TOKEN, user_name)

                        whatsapp = WhatsAppHandler(assistant_response, WHATSAPP_TOKEN, WHATSAPP_VERSION, phone_number_id, user_name, client, phone_number, message_id)
                        
                        assistant_response = interact.interact_w_ass1(
                            payload={
                                "type": "document",
                                "content": file_content,
                            })
                        response = await whatsapp.send_whatsapp_message()
                        await whatsapp.close_session()
                        return web.json_response({"response": f"{response}","status": "success"})
                        
                    else:
                        print(f"Failed to download document. Status code: {response.status_code}")
                        return web.json_response({"status": "error", "message": response}, status=response.status_code)
                
            

            # CUSTOMER COMES FROM ADS
            elif body['entry'][0]['changes'][0]['value']['messages'][0].get('referral'):
                # COLLECT DATA ON AD POST TO BETTER CONTEXT RESPONSE

                interact = Interact(phone_number, phone_number_id, client, WHATSAPP_VERSION, WHATSAPP_TOKEN, user_name)

                whatsapp = WhatsAppHandler(assistant_response, WHATSAPP_TOKEN, WHATSAPP_VERSION, phone_number_id, user_name, client, phone_number, message_id)
                
                source_url = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['source_url']
                source_type = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['source_type']
                source_id = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['source_id']
                headline = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['headline']
                ad_body = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['body']
                media_type = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['media_type']
                
                assistant_response = interact.interact_w_ass1(
                    payload={
                        "type": "from_ads",
                        "content": f"Greet customer that cliecked on advertisement. Advertisement information: Source url of the post the customer came from: {source_url}, Source type: {source_type}, Source ID: {source_id}, Headline of the ad: {headline}, Ad body: {ad_body}, Type of add: {media_type}"
                    })
                response = await whatsapp.send_whatsapp_message()
                await whatsapp.close_session()
                return web.json_response({"response": f"{response}","status": "success"})
                

            else:
                # FOR INTERACTIVE MESSASGES REPLIES
                interactive_msg = body['entry'][0]['changes'][0]['value']['messages'][0].get('interactive')

                interact = Interact(phone_number, phone_number_id, client, WHATSAPP_VERSION, WHATSAPP_TOKEN, user_name)

                # FOR BUTTON REPLIES
                if interactive_msg and 'button_reply' in interactive_msg:
                    # button_reply_id = interactive_msg['button_reply']['id']
                    assistant_response = interact.interact_w_ass1(
                        payload={
                            'type': "button_reply",
                            'text': interactive_msg['button_reply']['title']
                            })
                    whatsapp = WhatsAppHandler(assistant_response, WHATSAPP_TOKEN, WHATSAPP_VERSION, phone_number_id, user_name, client, phone_number, message_id)
                    response = await whatsapp.send_whatsapp_message()
                    await whatsapp.close_session()
                    return web.json_response({"response": f"{response}","status": "success"})

        return web.json_response({'message': 'ok'})
    else:
        return web.json_response({'message': 'error | unexpected body'}, status=400)

    


def home():
    return jsonify({
        'success': True,
        'status': 'healthy',
        'error': None
    })

tracemalloc.start()


# import logging

# logging.basicConfig(level=logging.DEBUG)


app = web.Application()
app.add_routes([web.get('/webhook', get_verify)])
app.add_routes([web.post('/webhook', webhook)])
app.add_routes([web.get('/', home)])


# asyncio.run(main())


if __name__ == '__main__':
    port = 3000
    web.run_app(app, port=port)