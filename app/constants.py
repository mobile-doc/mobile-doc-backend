import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME")
VERSION_NAME = os.getenv("_VERSION_NAME")

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GAE_VERSION = os.getenv("GAE_VERSION")
GAE_MEMORY_MB = os.getenv("GAE_MEMORY_MB")


PROJECT_NAME = "Dummy Project Name" if not PROJECT_NAME else PROJECT_NAME
VERSION_NAME = "Dummy Version" if not VERSION_NAME else VERSION_NAME
