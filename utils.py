import requests
from fastapi.encoders import jsonable_encoder
import slugify
from config import TELEGRAM_API_KEY, TELEGRAM_CHAT_ID, MOBIZON_API_KEY
import urllib.parse


def get_list_from_result(result):
    list = []
    for key, product in enumerate(result.fetchall()):
        list.append(jsonable_encoder(product[0]))

    return list


def to_slug(string: str):
    return slugify.slugify(string, allow_unicode=False)


def send_message(text):
    token = TELEGRAM_API_KEY
    chat_id = TELEGRAM_CHAT_ID

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text,
    }
    
    requests.get(url, params=params)


def send_otp(recipient: str, otp: int):
    token = MOBIZON_API_KEY

    text = f"Ваш код верификации для thaihana.kz: {otp}"
    text = urllib.parse.quote(text)

    url = f"https://api.mobizon.kz/service/message/sendsmsmessage?recipient={recipient}&text={text}&apiKey={token}"

    resp = requests.get(url)
