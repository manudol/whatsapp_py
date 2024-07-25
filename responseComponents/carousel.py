import requests
import re
import csv

from load_env import load_vars
import os


load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')

async def carousel(assistant_text, phone_number, phone_number_id):

    numbers = re.findall(r'\[(\d+)\]', assistant_text)
    numbers = [int(num) for num in numbers]

    csv_file = "./databases/products_db.csv"

    for number in numbers:
        with open(csv_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                records = []
                if row['product id'] == number:
                    records.append({'product_name': row['name'], 'product_image_url': row['image_url'], 'product_url': row['product_URLs'], 'descriptions': row['description']})
  

    url_count = len(numbers)

    print(numbers)
    print(records)
    print(url_count)

    # Initialize lists to store the extracted information
    names = []
    image_urls = []
    urls = []
    image_ids = []
    s_descriptions = []

    # Iterate over the JSON data to extract the required information
    for record in records:
        names.append(record["name"])
        image_urls.append(record["image_url"])
        urls.append(record["product_URLs"])
        s_descriptions.append(record['descriptions'])

    for image_url in image_urls:
        url1 = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/media'
        headers1 = {
            'Authorization': f'Bearer {WHATSAPP_TOKEN}'
        }
        files = {
            'file': f'{image_url}',
            'type': 'image/png',
            'messaging_product': 'whatsapp'
        }

        wa_file_upload = requests.post(url=url1, headers=headers1, files=files)
        wa_file_upload_json = wa_file_upload.json()
        image_id = wa_file_upload_json.get('id')
        image_ids.append(image_id)

    if url_count == 5:
        response = {
      "type": "CAROUSEL",
      "cards": [
        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[0]}",
              "example": {
                "header_handle": [f"{image_ids[0]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[0]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[0]}"}
              ]
            }
          ]
        },

        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[1]}",
              "example": {
                "header_handle": [f"{image_ids[1]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[1]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[1]}"}
              ]
            }
          ]
        },

        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[2]}",
              "example": {
                "header_handle": [f"{image_ids[2]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[2]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[2]}"}
              ]
            }
          ]
        },

        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[3]}",
              "example": {
                "header_handle": [f"{image_ids[3]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[0]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[3]}"}
              ]
            }
          ]
        },

        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[4]}",
              "example": {
                "header_handle": [f"{image_ids[4]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[4]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[4]}"}
              ]
            }
          ]
        }]
        }
        
    elif url_count == 4:
        response = {
      "type": "CAROUSEL",
      "cards": [
        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[0]}",
              "example": {
                "header_handle": [f"{image_ids[0]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[0]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[0]}"}
              ]
            }
          ]
        },

        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[1]}",
              "example": {
                "header_handle": [f"{image_ids[1]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[1]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[1]}"}
              ]
            }
          ]
        },

        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[2]}",
              "example": {
                "header_handle": [f"{image_ids[2]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[2]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[2]}"}
              ]
            }
          ]
        },

        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[3]}",
              "example": {
                "header_handle": [f"{image_ids[3]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[0]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[3]}"}
              ]
            }
          ]
        }
        ]
        }
    elif url_count == 3:
        response = {
      "type": "CAROUSEL",
      "cards": [
        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[0]}",
              "example": {
                "header_handle": [f"{image_ids[0]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[0]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[0]}"}
              ]
            }
          ]
        },

        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[1]}",
              "example": {
                "header_handle": [f"{image_ids[1]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[1]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[1]}"}
              ]
            }
          ]
        },

        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[2]}",
              "example": {
                "header_handle": [f"{image_ids[2]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[2]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[2]}"}
              ]
            }
          ]
        }
        ]
        }
    elif url_count == 2:
        response = {
      "type": "CAROUSEL",
      "cards": [
        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[0]}",
              "example": {
                "header_handle": [f"{image_ids[0]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[0]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[0]}"}
              ]
            }
          ]
        },

        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[1]}",
              "example": {
                "header_handle": [f"{image_ids[1]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[1]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[1]}"}
              ]
            }
          ]
        }
        ]
        }
    elif url_count == 1:
        response = {
      "type": "CAROUSEL",
      "cards": [
        {
          "components": [
            {
              "type": "HEADER",
              "format": f"{names[0]}",
              "example": {
                "header_handle": [f"{image_ids[0]}"]
              }
            },
            {
              "type": "BODY",
              "text": f"{s_descriptions[0]}"
            },
            {
              "type": "BUTTONS",
              "buttons": [
                {
                  "type": "URL",
                  "text": "Shop Now",
                  "url": f"{url[0]}"}
                  ]
                }
              ]
            }
          ]
        }
    else:
        response = "error: No URLs found or number of URLs is unsupported."
    print(response)

    
    url = f'https://graph.facebook.com/{WHATSAPP_VERSION}/{phone_number_id}/messages'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHATSAPP_TOKEN}'
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": f"{phone_number}",
        "type": "template",
        "template": {
          "name": "summer_carousel_promo_2023",
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
          response
    ]
  }
}

    api_response = requests.post(url, headers=headers, data=data)

    return api_response.json()