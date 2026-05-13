import os
from dotenv import load_dotenv

load_dotenv()


def get_required(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise ValueError(f"{key} not set in .env file")
    return val


class Config:
    TG_API_ID: int = int(get_required("TG_API_ID"))
    TG_API_HASH: str = get_required("TG_API_HASH")
    TG_ALLOWED_USERS: list[int] = [
        int(x.strip()) for x in get_required("TG_ALLOWED_USERS").split(",")
    ]

    GA_INSTANCE_ID: str = get_required("GA_INSTANCE_ID")
    GA_API_TOKEN: str = get_required("GA_API_TOKEN")
    GA_API_URL: str = os.getenv("GA_API_URL", "https://api.green-api.com/v3")
    GA_MEDIA_URL: str = os.getenv("GA_MEDIA_URL", "https://media.green-api.com/v3")
    MAX_TARGET_PHONE: str = get_required("MAX_TARGET_PHONE")

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
