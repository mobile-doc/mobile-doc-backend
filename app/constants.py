import os
from dotenv import load_dotenv
import json
import logging

# Load environment variables from .env
load_dotenv()

PROJECT_NAME = "Mobile Doc Backend"
VERSION_NAME = os.getenv("GAE_VERSION")
VERSION_NAME = "dev" if not VERSION_NAME else VERSION_NAME
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

try:
    with open("credential.json", "r") as file:
        data = json.load(file)
        atlas_password = data.get("_ATLAS_PASSWORD")
        atlas_username = data.get("_ATLAS_USERNAME")
except:
    logging.log("Couldn't read from 'credential.json'")
    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            file_path = os.path.join(root, file)
            print(file_path)
