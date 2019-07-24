import os
from dotenv import load_dotenv
load_dotenv()

class config(object):
    def get(var):
        return os.getenv(var)
