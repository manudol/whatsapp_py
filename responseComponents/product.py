import os
import httpx
import certifi
import ssl
from io import BytesIO
from PIL import Image

from load_env import load_vars

from interactObjects.djangoInteract import Getters

load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')
BACKEND_URL = os.getenv('BACKEND_URL')


# (WORKS!)
async def product(ai_output, phone_number, phone_number_id, access_token, business_id):
    getters = Getters(access_token, business_id, phone_number_id)
    
    name, description, image_url, price = await getters.get_product(ai_output)
    
    # First download the image locally
    image_file_path = f"product_image_{os.urandom(8).hex()}.jpg"
    ctx = ssl.create_default_context(cafile=certifi.where())
    
    try:
        # Download the image
        async with httpx.AsyncClient(verify=ctx) as client1:
            response = await client1.get(image_url)
            if response.status_code == 200:
                # Process the image to ensure it meets WhatsApp requirements
                try:
                    # Load image into PIL
                    img = Image.open(BytesIO(response.content))
                    
                    # Convert to RGB mode (removing alpha channel if present)
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Save as JPEG with high quality
                    img.save(image_file_path, 'JPEG', quality=95)
                except Exception as img_error:
                    print(f"Error processing image: {str(img_error)}")
                    raise
                
                # Upload the image to WhatsApp
                upload_url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/media'
                headers = {
                    'Authorization': f'Bearer {WHATSAPP_TOKEN}',
                }
                
                with open(image_file_path, 'rb') as f:
                    # Prepare multipart form data
                    files = {
                        'file': (os.path.basename(image_file_path), f, 'image/jpeg')
                    }
                    data = {
                        'messaging_product': 'whatsapp',
                        'type': 'image/jpeg'
                    }
                    
                    # Send the upload request
                    async with httpx.AsyncClient(verify=ctx) as upload_client:
                        upload_response = await upload_client.post(
                            upload_url,
                            headers=headers,
                            data=data,
                            files=files
                        )
                    
                    upload_data = upload_response.json()
                    
                    if 'error' in upload_data:
                        print(f"Upload error: {upload_data}")
                        raise Exception(f"Media upload failed: {upload_data.get('error', {}).get('message', 'Unknown error')}")
                    
                    media_id = upload_data['id']
                    print("\n\n123 media_id: ", media_id)
                    
                    # Send the message with the media ID
                    url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
                    }
                    data = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": f"{phone_number}",
                        "type": "image",
                        "image": {
                            "id": media_id,
                            "caption": f"{name}\n{description}\n{price}"
                        }
                    }
                    
                    async with httpx.AsyncClient(verify=ctx) as client2:
                        response = await client2.post(url, headers=headers, json=data)
                    
                    # Clean up the temporary file
                    if os.path.exists(image_file_path):
                        os.remove(image_file_path)

                    print("\n\n123456 response: ", response.json())
                    return response.json()
            else:
                # Fallback if image download fails
                url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {WHATSAPP_TOKEN}'
                }
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": f"{phone_number}",
                    "type": "text",
                    "text": {
                        "body": f"{name}\n{description}\n{price}"
                    }
                }
                async with httpx.AsyncClient(verify=ctx) as client2:
                    response = await client2.post(url, headers=headers, json=data)
                return response.json()
    except Exception as e:
        print(f"Error in product function: {str(e)}")
        # Clean up in case of error
        if os.path.exists(image_file_path):
            os.remove(image_file_path)
        
        # Send text-only message as fallback
        url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {WHATSAPP_TOKEN}'
        }
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": f"{phone_number}",
            "type": "text",
            "text": {
                "body": f"{name}\n{description}\n{price}"
            }
        }
        async with httpx.AsyncClient(verify=ctx) as client2:
            response = await client2.post(url, headers=headers, json=data)
            return response.json()
