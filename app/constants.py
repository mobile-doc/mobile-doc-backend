import os
from dotenv import load_dotenv
import json

# Load environment variables from .env
load_dotenv()

PROJECT_NAME = "Mobile Doc Backend"
VERSION_NAME = os.getenv("GAE_VERSION")
VERSION_NAME = "dev" if not VERSION_NAME else VERSION_NAME
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

with open("credential.json", "r") as file:
    data = json.load(file)
    atlas_password = data.get("_ATLAS_PASSWORD")
    atlas_username = data.get("_ATLAS_USERNAME")
