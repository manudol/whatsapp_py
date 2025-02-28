import os
import httpx
import certifi
import ssl
import re

from openai_client.client import client

from .error_response import error_response

from load_env import load_vars

load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')
BACKEND_URL = os.getenv('BACKEND_URL')


async def db_call(words:list, access_token:str, business_id:str) -> list[bool, dict]:
    response = ""
    url = BACKEND_URL+"/flows/product/"+str(business_id)+"/get_product/"
    headers = {
                "Authorization": "Bearer "+access_token,
                "Content-type": "application/json",
                "Accept": "application/json"
               }
    params = {
        "searchFor": words
    }
    
    async with httpx.AsyncClient() as client1:
        response = await client1.get(url, headers=headers, params=params)
    if response.json()['success']:
        return response.json()['product'], True
    else:
        return None, False



async def load_products(product_string, access_token, business_id):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You will be given a product name, price and description. You will have to extract the keywords only.\
             for exmaple if the product name is 'apple' and the price is '10' and the description is 'a red apple' you will have to extract and output 'apple 10 red'.\
             Only output the keywords, do not output anything else."},
            {"role": "user", "content": "Here is what the assistant wants to recommend extract the keywords only: "+product_string}
        ]
    )
    words = response.choices[0].message.content.split(' ')
    product_infos, b = await db_call(words, access_token, business_id)
    if b:
        return product_infos, True
    else: raise ValueError("Product recommendation failed.")




# (WORKS!)
async def product(ai_output, phone_number, phone_number_id, access_token, business_id):
    pattern = r'PRODUCT NAME:(.*?)\s*\|\s*PRODUCT PRICE:(.*?)\s*\|\s*PRODUCT DESCRIPTION:(.*?)(?:\s*$|\s*\|)'
    match = re.search(pattern, ai_output)
    if match:
        product_name = match.group(1)
        product_price = match.group(2)
        product_description = match.group(3)

        product_infos, b = await load_products(product_name+product_price+product_description, access_token, business_id)

        if b:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Write a well formatted description for the product, based on the product infos received.\
                    The description should not contain all the infos and present the infos in a way that is easy to read for the user."},
                    {"role": "user",
                    "content": f"Right a descrition for this product: \
                        Product name: {product_infos['name']} \
                        Product description: {product_infos['description']} \
                        Product price: {product_infos['price']} \
                        Product reduction: {product_infos['reduction']} \
                        Product price after reduction: {product_infos['price_after_reduction']} \
                        Product link: {product_infos['link']}"
                    }
                ]
            )
            
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
                    "link": product_infos['image_url'],
                    "caption": response.choices[0].message.content
                    }
                }
            ctx = ssl.create_default_context(cafile=certifi.where())
            async with httpx.AsyncClient(verify=ctx) as client2:
                response = await client2.post(url, headers=headers, json=data)
                return await response.json(), await client2.aclose()
        else: 
            res = await error_response(phone_number, phone_number_id)
            return res