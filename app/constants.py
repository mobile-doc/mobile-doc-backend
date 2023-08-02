import os

PROJECT_NAME = os.getenv("_PROJECT_NAME")
VERSION_NAME = os.getenv("_VERSION_NAME")

SHORT_SHA = os.getenv("_SHORT_SHA")
BRANCH_NAME = os.getenv("_BRANCH_NAME")
REPO_NAME = os.getenv("_REPO_NAME")


PROJECT_NAME = "Dummy Project Name" if not PROJECT_NAME else PROJECT_NAME
VERSION_NAME = "Dummy Version" if not VERSION_NAME else VERSION_NAME
