from load_env import load_vars
import tracemalloc

import os
import requests
import base64
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from openai_client.client import client
from interactObjects.interact import Interact
from interactObjects.whatsappInteract import WhatsAppHandler
from interactObjects.djangoInteract import DjangoInteract, DjangoAccess


load_vars()


BACKEND_URL = os.getenv("BACKEND_URL")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_VERSION = os.getenv("WHATSAPP_VERSION")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


app = FastAPI()


@app.get("/webhook")
async def get_verify(request: Request):
    print("request: ", request)
    hub_mode = request.query_params.get('hub.mode')
    hub_verify_token = request.query_params.get('hub.verify_token')
    hub_challenge = request.query_params.get('hub.challenge')
    print("hub_mode: ", hub_mode)
    print("hub_verify_token: ", hub_verify_token)
    print("hub_challenge: ", hub_challenge)
    if hub_mode and hub_verify_token:
        if hub_mode == 'subscribe' and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
            print("WEBHOOK VERIFIED")
            return int(hub_challenge)
        else:
            raise HTTPException(status_code=403)
    else:
        raise HTTPException(status_code=400)


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    object = body.get('object')
    if object:
        # Initialize variables to None or an empty list for safety
        is_a_read_confirm = None
        is_message = None

        # Check if payload has "statuses" field to confirm read receipt
        if body.get('entry') and body['entry'][0].get('changes') and body['entry'][0]['changes'][0].get('value') and 'statuses' in body['entry'][0]['changes'][0]['value']:
            is_a_read_confirm = body['entry'][0]['changes'][0]['value']['statuses']

        # Check if payload has "messages" field to confirm message type
        elif body.get('entry') and body['entry'][0].get('changes') and body['entry'][0]['changes'][0].get('value') and 'messages' in body['entry'][0]['changes'][0]['value']:
            is_message = body['entry'][0]['changes'][0]['value']['messages']
        
        print("Other body to be parsed: ", body)
        
        if is_message:
            print("is message !!!!!!!!! ", is_message)
            # Customer's phone number:
            phone_number = body['entry'][0]['changes'][0]['value']['messages'][0]['from']

            # Customer's last message id:
            message_id = body['entry'][0]['changes'][0]['value']['messages'][0]['id']

            # Customer's Whastapp User Name :
            user_name = body['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
            
            # Organisor's business id
            business_id = body['entry'][0]['id']

            print("business_id: ", business_id)

            # WHATSAPP BUSINESS PHONE NUMBER ID for the url Endpoint
            phone_number_id = body['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']

            django_access = DjangoAccess(phone_number_id, business_id, phone_number)

            ( model_id, 
              system_prompt, 
              thread_id, 
              access_token, 
              basemodel_job_id ) = await django_access.get_modelID_and_conversation()
            
            print("model_id 123: ", model_id)


            interact = Interact(phone_number, phone_number_id, model_id, user_name, access_token, system_prompt, thread_id)
            whatsapp = WhatsAppHandler(phone_number_id, phone_number, message_id, access_token, business_id)
            dj_interact = DjangoInteract(access_token, basemodel_job_id, model_id, phone_number, user_name, business_id, thread_id)


            #FOR TEXT (WORKS!)
            if body['entry'][0]['changes'][0]['value']['messages'][0].get('text'):
                print("Text received!")
                user_message = body['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']

                assistant_response = interact.messageAI(payload={
                        "type": "text",
                        "text": user_message
                })

                print("Assistant Response: ", assistant_response)

                try:
                    response = await whatsapp.message_wa(assistant_response, user_message)
                    await dj_interact.save_messages(
                                        user_message=response["user_message"], 
                                        assistant_message=response["assistant_message"],
                                        output_type=response["output_type"],
                                        double_message=response["double_message"]
                                        )
                    
                    return JSONResponse(content={"status": "message sent", "response": response}, status_code=202)
                
                except ValueError as err:
                    print(err.args)
                    return JSONResponse(content={"status": f"{err}"}, status_code=400)
                   


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
                        return JSONResponse(content={"status": "already processing"}, status_code=202)
            
                    except ValueError as err:
                        print(err.args)
                        return JSONResponse(content={"status": f"{err}"}, status_code=400)
                        

            
            
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
                        return JSONResponse(content={"status": "already processing"}, status_code=202)
                        
                    except ValueError as err:
                        print(err.args)
                        return JSONResponse(content={"status": f"{err}"}, status_code=400)


            # (WORKS!)   
            elif body['entry'][0]['changes'][0]['value']['messages'][0].get('location'):
                location_info = body['entry'][0]['changes'][0]['value']['messages'][0].get('location')
                if location_info:
                    longitude = location_info['longitude']
                    latitude = location_info['latitude']

                    user_message = f"Customer sent {longitude} and {latitude}"

                    assistant_response = interact.messageAI(payload={
                    "type": "location_send",
                    "text": f"Customer just responded with their location:\
                                Longitude: {longitude},\
                                latitude: {latitude}"
                    })


                    print("Assistant Response: ", assistant_response)
               
                    try:
                        await whatsapp.message_wa(assistant_response, user_message)
                        return JSONResponse(content={"status": "already processing"}, status_code=202)
                    
                    except ValueError as err:
                            print(err.args)
                            return JSONResponse(content={"status": f"{err}"}, status_code=400)
                    

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
                    return JSONResponse(content={"status": "already processing"}, status_code=202)
                        
                except ValueError as err:
                    print(err.args)
                    return JSONResponse(content={"status": f"{err}"}, status_code=400)
            else:
                # FOR INTERACTIVE MESSASGES REPLIES
                interactive_msg = body['entry'][0]['changes'][0]['value']['messages'][0].get('interactive')


                # (WORKS)
                # FOR BUTTON REPLIES
                if interactive_msg and 'button_reply' in interactive_msg:
                    
                    assistant_response = interact.messageAI(
                        payload={
                            'type': "button_reply",
                            'text': f"Customer clicked on buttons choice: {interactive_msg['button_reply']['title']}"
                            })
                    
                    user_message = interactive_msg['button_reply']['title']

                    try:
                        await whatsapp.message_wa(assistant_response, user_message)
                        return JSONResponse(content={"status": "already processing"}, status_code=202)
                    
                    except ValueError as err:
                        print(err.args)
                        return JSONResponse(content={"status": f"{err}"}, status_code=400)
                else:
                    print("Message type not authorized by the system.")
                    return JSONResponse(content={'message': 'Unauthorized message.'})    
        
        # (WORKS!)
        elif is_a_read_confirm:
            print(f"message read confirmation.")
            return JSONResponse(content={'status': 'read'})

        else:
            print("Message type not authorized by the system.")
            return JSONResponse(content={'message': 'Unauthorized message.'})    
    else:
        return JSONResponse(content={'message': 'error | unexpected body'}, status_code=400)

    

@app.get("/")
def home():
    return JSONResponse(content={
        'success': True,
        'status': 'healthy',
        'error': None
    })

tracemalloc.start()


if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 7000))
    host = os.environ.get('HOST', 'localhost')
    try:
        uvicorn.run(app, host=host, port=port)
    except OSError as e:
        print(f"Failed to start server on {host}:{port}")
        print(f"Error: {e}")
        raise