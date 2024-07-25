import requests

from load_env import load_vars
import os
import asyncio

load_vars()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_VERSION = os.getenv('WHATSAPP_VERSION')

async def flows(assistant_text, phone_number, phone_number_id, message_id):
    pass