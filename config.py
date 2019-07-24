import os
from dotenv import load_dotenv
load_dotenv()

NODE_NAME   = os.getenv("NODE_NAME")

KB_URL      = os.getenv("KB_URL")
KB_USERNAME = os.getenv("KB_USERNAME")
KB_PASSWORD = os.getenv("KB_PASSWORD")
