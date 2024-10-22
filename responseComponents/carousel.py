import aiohttp
import asyncio
import certifi
import ssl
import re
from load_env import load_vars
import os
import csv
import time
import random

load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')
FILES_DIRECTORY = "./downloaded_images"

ssl_context = ssl.create_default_context(cafile=certifi.where())


async def upload_file(session, file_path, phone_number_id):
    try:
        # Extract the file name
        file_name = os.path.basename(file_path)
        # Determine the MIME type based on the file extension (this is simplified for images)
        mime_type = "image/jpeg" if file_name.endswith(".jpg") else "image/png"  # Adjust if necessary

        # Prepare the form data for the request
        form_data = aiohttp.FormData()
        form_data.add_field('file', open(file_path, 'rb'), filename=file_name)
        form_data.add_field('type', mime_type)
        form_data.add_field('messaging_product', 'whatsapp')

        url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/media'

        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

        # session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))

        # Make the POST request to WhatsApp API
        async with session.post(url, headers=headers, data=form_data, ssl_context=ssl_context) as response:
            # Parse the JSON response to get the media ID
            if response.status == 200:
                result = await response.json()
                return result['id']
            else:
                print(f"Failed to upload {file_name}: {response.status}")
                return None
    except Exception as e:
        print(f"Error uploading {file_name}: {str(e)}")
        return None



async def upload_files(file_list, phone_number_id):
    async with aiohttp.ClientSession() as session:
        tasks = []
        # Loop over the file list and create a task for each upload
        for file_name in file_list:
            file_path = os.path.join(FILES_DIRECTORY, file_name)
            tasks.append(upload_file(session, file_path, phone_number_id))
        
        # Run all the tasks concurrently
        media_ids = await asyncio.gather(*tasks)
        return media_ids
    


async def carousel(assistant_text, phone_number_id, phone_number):
    print("Assistant text received for carousel: ", assistant_text)

    numbers = re.findall(r'\[(\d+)\]', assistant_text)
    numbers = [int(num) for num in numbers]

    print("Product IDs", numbers)

    csv_file = "./databases/products_db.csv"

    # Initialize lists to store the extracted information
    names = []
    image_files = []
    urls = []

    # existing_files = os.listdir('downloaded_images')

    for num in numbers:
        image_files.append(f"{num}.jpg")

    # .... Not done from here ....

    with open(csv_file) as file:
        csv_reader = csv.reader(file)
        records=[row for idx, row in enumerate(csv_reader) if idx in (numbers)]


    for i in range(len(numbers)):
        if i < len(records):
            if len(records[i]) > 1:
                urls.append(records[i][1])
                names.append(records[i][3])
            pass
        else:
            print(f"Index {i} is out of range for records.")
    
    print("URLs", urls)
    print("Names", names)
    print("image files", image_files)

    image_ids = await upload_files(image_files, phone_number_id)

    print("Image IDs: ", image_ids)

    cards = []
    for i in range(len(numbers)):
        card2 = {
        "card_index": i,
        "components": [
        {
            "type": "HEADER",
            "parameters": [
            {
                "type": "IMAGE",
                "image": {
                "id": f"{image_ids[i]}"
                }
            }
            ]
        },
        {
            "type": "BODY",
            "parameters": [
            {
                "type": "text",
                "text": f"{names[i]}"
            }
            ]
        },
        {
            "type": "BUTTON",
            "sub_type": "URL",
            "index": "BUTTON_INDEX",
            "parameters": [
            {
                "type": "PAYLOAD",
                "payload": "product_123"
                },
                {
                "type": "URL",
                "value": f"{urls[i]}"
                }
                ]
                }
            ]
        }
        cards.append(card2)

    response = {
        "type": "CAROUSEL",
        "cards": cards
    }

    url1 = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/message_templates'
    headers1 = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }

    numbers = [1, 2, 3, 4, 5, 6, 7, 8 , 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    carousel_id = round(int(random.choice(numbers))*float(time.time())/int(random.choice(numbers)))

    data1 = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": f"carousel-{carousel_id}",
            "language": {
                "code": "en_US"
            },
            "components": [
                {
                    "type": "BODY",
                    "parameters": [
                        {
                            "type": "TEXT",
                            "text": "20OFF"
                        },
                        {
                            "type": "TEXT",
                            "text": "20%"
                        }
                    ]
                },
                response,
            ]
        }
    }
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    session = aiohttp.ClientSession()

    async with session.post(url1, headers=headers1, json=data1, ssl_context=ssl_context) as response:
        return await response.json()
