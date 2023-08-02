import os

PROJECT_NAME = os.getenv("PROJECT_NAME")
VERSION_NAME = os.getenv("VERSION_NAME")


PROJECT_NAME = "Dummy Project Name" if not PROJECT_NAME else PROJECT_NAME
VERSION_NAME = "Dummy Version" if not VERSION_NAME else VERSION_NAME
