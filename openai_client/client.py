from openai import OpenAI
from load_env import load_vars
import os

load_vars()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
