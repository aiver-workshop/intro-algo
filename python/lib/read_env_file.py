# pip install python-dotenv
import os
from dotenv import load_dotenv

# create a .env to stores <key>=<value>, for example secret=abc
dotenv_path = 'c:/vault/.env'
load_dotenv(dotenv_path=dotenv_path)
print(os.getenv('secret'))
