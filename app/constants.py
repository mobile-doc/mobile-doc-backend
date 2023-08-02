import os

PROJECT_NAME = os.getenv("PROJECT_NAME")
VERSION_NAME = os.getenv("VERSION_NAME")

SHORT_SHA = os.getenv("SHORT_SHA")
BRANCH_NAME = os.getenv("BRANCH_NAME")
REPO_NAME = os.getenv("REPO_NAME")


PROJECT_NAME = "Dummy Project Name" if not PROJECT_NAME else PROJECT_NAME
VERSION_NAME = "Dummy Version" if not VERSION_NAME else VERSION_NAME
