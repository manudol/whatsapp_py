from load_env import load_vars
# from save_img import execute_download
import tracemalloc

import os
import base64
import requests
from openai import OpenAI
from aiohttp import web

from interactObjects.interact import Interact
from interactObjects.processDocs import ProcessDocs
from interactObjects.whatsappInteract import WhatsAppHandler

load_vars()

# execute_download()


WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_VERSION = os.getenv("WHATSAPP_VERSION")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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
        # Check if body is a read confirmation or not:
        is_a_read_confirm = body.get('entry', [])[0].get('changes', [])[0].get('value', {}).get('statuses', []).get('status', {})
        if is_a_read_confirm: return 0
        
        # IF MESSAGE DOES NOT COME FROM BUTTON
        is_not_interactive = body.get('entry', [])[0].get('changes', [])[0].get('value', {}).get('messages', [])
        
        # WHATSAPP BUSINESS PHONE NUMBER ID for the url Endpoint
        phone_number_id = body['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']

        print("Phone Number ID: ", phone_number_id)

        # Customer's phone number:
        phone_number = body['entry'][0]['changes'][0]['value']['messages'][0]['from']

        # Customer's Whastapp User Name :
        user_name = body['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
        
        message_id = body['entry'][0]['changes'][0]['value']['messages'][0]['id']
        print('Message ID: ', message_id)
        
        interact = Interact(phone_number, phone_number_id, client, user_name)

        whatsapp = WhatsAppHandler(phone_number_id, phone_number, message_id)
        
        
        if is_not_interactive:

            #FOR TEXT (WORKS!)
            if body['entry'][0]['changes'][0]['value']['messages'][0].get('text'):
                 
               user_message = body['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']


               assistant_response = interact.messageAI(payload={
                    "type": "text",
                    "text": user_message
               })

               print("Assistant Response: ", assistant_response)

               
               
               try:
                   await whatsapp.message_wa(assistant_response, user_message)
                   return web.json_response({"status": "already processing"}, status=202)
               
               except ValueError as err:
                    print(err.args)
                    return web.json_response({"status": f"{err}"}, status=400)
                   
                    



            #FOR AUDIO (WORKS!)
            elif body['entry'][0]['changes'][0]['value']['messages'][0].get('audio'):
                if body['entry'][0]['changes'][0]['value']['messages'][0]['audio'].get('voice'):
                    print("Audio response received!\n")
                    print(body['entry'][0]['changes'][0]['value']['messages'][0]['audio']['id'])
                    media_url_response = requests.get(
                        url=f"https://graph.facebook.com/{WHATSAPP_VERSION}/{body['entry'][0]['changes'][0]['value']['messages'][0]['audio']['id']}",
                        headers={
                            'Authorization': f'Bearer {WHATSAPP_TOKEN}',
                        }
                    )
                    
                    print("Media url api response: ", media_url_response)


                    media_url = media_url_response.json()['url']

                    print("Media url: ", media_url)

                    rnd_file_name = f"audio_{os.urandom(8).hex()}.ogg"
                    audio_response = requests.get(media_url, headers={'Authorization': f'Bearer {WHATSAPP_TOKEN}'}, stream=True)

                    with open(rnd_file_name, 'wb') as f:
                        for chunk in audio_response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    
                    
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=open(rnd_file_name, 'rb'),
                        response_format="text"
                    )
                    
                    os.remove(rnd_file_name)

                    
                    assistant_response = interact.messageAI(
                        payload={
                            'type': 'audio',
                            'text': transcription,
                        }
                    )
                    
                    try:
                        await whatsapp.message_wa(assistant_response)
                        return web.json_response({"status": "already processing"}, status=202)
            
                    except ValueError as err:
                        print(err.args)
                        return web.json_response({"status": f"{err}"}, status=400)
                        

            
            
            
            # FOR IMAGE (WORKS!)
            elif body['entry'][0]['changes'][0]['value']['messages'][0].get('image'):
                if body['entry'][0]['changes'][0]['value']['messages'][0]['type'] == 'image':
                    print("Image received!")
                    print(body['entry'][0]['changes'][0]['value']['messages'][0]['image']['id'])
                    media_response = requests.get(
                        f"https://graph.facebook.com/{WHATSAPP_VERSION}/{body['entry'][0]['changes'][0]['value']['messages'][0]['image']['id']}",
                        headers={
                            'Authorization': f'Bearer {WHATSAPP_TOKEN}'
                        }
                    )

                    wa_img_url = media_response.json()['url']
                    wa_img_type = media_response.json()['mime_type']


                    if wa_img_type == "image\/jpeg":
                        mime_type = "image/jpeg"
                        
                    elif wa_img_type == "image\/png":
                        mime_type = "image/png"

                    
                    image_file_name = f"image_{os.urandom(8).hex()}.jpeg"

                    response = requests.get(wa_img_url, headers={'Authorization': f'Bearer {WHATSAPP_TOKEN}'}, stream=True)

                    if response.status_code == 200:
                        # Save the image file
                        with open(image_file_name, 'wb') as file:
                            for chunk in response.iter_content(1024):
                                file.write(chunk)
                                
                    else:

                        print(f"Failed to download image. Status code: {response.status_code}")

                    with open(image_file_name, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    
                    
                    image_vision = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Give a clear description of the image that you see. Start your answer by: '{This is the image that the customer sent.}. Including the brackets please.'",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url":  f"data:{mime_type};base64,{base64_image}"
                                        }, 
                                    },
                                ],
                            }
                        ],
                    )
                    image_transcript = image_vision.choices[0]
                    
                    os.remove(image_file_name)


                    assistant_response = interact.messageAI(
                                payload={
                                    'type': 'image',
                                    'text': image_transcript,
                                }
                            )
                    
                    try:
                        await whatsapp.message_wa(assistant_response)
                        return web.json_response({"status": "already processing"}, status=202)
                        
                    except ValueError as err:
                        print(err.args)
                        return web.json_response({"status": f"{err}"}, status=400)


            # Bad idea to send it to assistant
            # Better idea to store it in CRM
            # FOR DOCUMENTS
            # elif body['entry'][0]['changes'][0]['value']['messages'][0].get('document'):
            #     document_info = body['entry'][0]['changes'][0]['value']['messages'][0].get('document')
            #     if document_info:
            #         document_id = document_info['id']
            #         mime_type = document_info['mime_type']
            #         filename = document_info['filename']
            #         # Step 2: Download the document
            #         document_url = f"https://graph.facebook.com/{WHATSAPP_VERSION}/{document_id}"
            #         headers = {
            #             'Authorization': f'Bearer {WHATSAPP_TOKEN}'
            #         }
            #         response = requests.get(document_url, headers=headers)
            #         if response.status_code == 200:
            #             with open(filename, 'wb') as file:
            #                 file.write(response.content)
            #             print(f"Document {filename} downloaded successfully.")

            #         # Step 3: Process the document
            #             doc_process = ProcessDocs(filename, mime_type)
            #             file_content = doc_process.process_document(filename, mime_type)
                        
            #             interact = Interact(phone_number, phone_number_id, client, WHATSAPP_VERSION, WHATSAPP_TOKEN, user_name)

            #             whatsapp = WhatsAppHandler(assistant_response, WHATSAPP_TOKEN, WHATSAPP_VERSION, phone_number_id, user_name, client, phone_number, message_id)
                        
            #             assistant_response = interact.interact_w_ass1(
            #                 payload={
            #                     "type": "document",
            #                     "content": file_content,
            #                 })
            #             response = await whatsapp.send_whatsapp_message()
            #             await whatsapp.close_session()
            #             return web.json_response({"response": f"{response}","status": "success"})
                        
            #         else:
            #             print(f"Failed to download document. Status code: {response.status_code}")
            #             return web.json_response({"status": "error", "message": response}, status=response.status_code)
                
            

            # CUSTOMER COMES FROM ADS - (SHOULD WORK!)
            elif body['entry'][0]['changes'][0]['value']['messages'][0].get('referral'):
                
                # COLLECT DATA ON AD POST TO BETTER CONTEXT RESPONSE
                source_url = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['source_url']
                source_type = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['source_type']
                source_id = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['source_id']
                headline = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['headline']
                ad_body = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['body']
                media_type = body['entry'][0]['changes'][0]['value']['messages'][0]['referral']['media_type']


                assistant_response = interact.messageAI(
                    payload={
                        "type": "from_ads",
                        "content": f"Greet customer that cliecked on advertisement. \
                            Advertisement information: Source url of the post the customer came from: {source_url},\
                            Source type: {source_type}, Source ID: {source_id}, \
                                Headline of the ad: {headline}, \
                                    Ad body: {ad_body}, \
                                        Type of add: {media_type}"
                    })
                
                try:
                    await whatsapp.message_wa(assistant_response)
                    return web.json_response({"status": "already processing"}, status=202)
                        
                except ValueError as err:
                    print(err.args)
                    return web.json_response({"status": f"{err}"}, status=400)
            else:
                print("Message type not authorized by the system.")
                return web.json_response({'message': 'Unauthorized message.'})    

        else:
            # FOR INTERACTIVE MESSASGES REPLIES
            interactive_msg = body['entry'][0]['changes'][0]['value']['messages'][0].get('interactive')


            # FOR BUTTON REPLIES
            if interactive_msg and 'button_reply' in interactive_msg:
                # button_reply_id = interactive_msg['button_reply']['id']
                assistant_response = interact.messageAI(
                    payload={
                        'type': "button_reply",
                        'text': interactive_msg['button_reply']['title']
                        })
                
                try:
                    await whatsapp.message_wa(assistant_response)
                    return web.json_response({"status": "already processing"}, status=202)
                        
                except ValueError as err:
                    print(err.args)
                    return web.json_response({"status": f"{err}"}, status=400)


            return web.json_response({'message': 'ok'})
    else:
        return web.json_response({'message': 'error | unexpected body'}, status=400)

    


def home():
    return web.json_response({
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


if __name__ == '__main__':
    port = 3000
    web.run_app(app, port=port)