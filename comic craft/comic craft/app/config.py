import os
from dotenv import load_dotenv

load_dotenv()

APP_MODE = os.getenv(
    "APP_MODE",
    "pollinations"
)

POLLINATIONS_API_KEY = os.getenv(
    "POLLINATIONS_API_KEY",
    ""
).strip()