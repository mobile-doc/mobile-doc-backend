import os


def create_env_file():
    with open(".env", "w") as f:
        f.write(f"PROJECT_NAME={os.getenv('This is a project name')}\n")
        # f.write(f"PROJECT_NAME={os.getenv('_PROJECT_NAME')}\n")
        f.write(f"VERSION_NAME={os.getenv('_VERSION_NAME')}\n")
        f.write(f"SHORT_SHA={os.getenv('_SHORT_SHA')}\n")
        f.write(f"BRANCH_NAME={os.getenv('_BRANCH_NAME')}\n")
        f.write(f"REPO_NAME={os.getenv('_REPO_NAME')}\n")


if __name__ == "__main__":
    create_env_file()
