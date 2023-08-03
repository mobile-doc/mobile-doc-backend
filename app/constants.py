import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

PROJECT_NAME = "Mobile Doc Backend"
VERSION_NAME = os.getenv("GAE_VERSION")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

atlas_password = os.getenv("_ATLAS_PASSWORD")
atlas_username = os.getenv("_ATLAS_USERNAME")
