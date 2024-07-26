from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = os.environ.get("DEBUG")

SECRET = os.environ.get("SECRET")

LIMIT = int(os.environ.get("LIMIT"))

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

IMAGE_PATH = os.environ.get("IMAGE_PATH")

MOBIZON_API_KEY = os.environ.get("MOBIZON_API_KEY")

RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY")