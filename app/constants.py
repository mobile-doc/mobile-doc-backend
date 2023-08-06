import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

PROJECT_NAME = "Mobile Doc Backend"
VERSION_NAME = os.getenv("GAE_VERSION")
VERSION_NAME = "dev" if not VERSION_NAME else VERSION_NAME
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

TAG_NAME = os.getenv("_TAG_NAME")
SHORT_SHA = os.getenv("_SHORT_SHA")
