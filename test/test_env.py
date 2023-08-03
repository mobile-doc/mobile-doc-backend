import os


def test_atlas():
    atlas_password = os.getenv("_ATLAS_PASSWORD")
    atlas_username = os.getenv("_ATLAS_USERNAME")

    print(f"{atlas_username=}, {atlas_password=}")
