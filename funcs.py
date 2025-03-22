import os
import httpx
import requests
from user_agents import parse

async def get_location(ip: str) -> tuple:
    try:
        url = f"https://ipinfo.io/{ip}/json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
        
        country_code = data.get("country", "")
        city = data.get("city", "")
        region = data.get("region", "")
        return (country_code, city, region)
    except:
        return (None, None, None)

def parse_user_agent(user_agent):
    user_agent_parse = parse(user_agent)
    return {
        'browser': user_agent_parse.browser.family,  # Браузер
        'browser_version': user_agent_parse.browser.version,  # Версия браузера
        'os': user_agent_parse.os.family,  # Операционная система
        'os_version' : user_agent_parse.os.version,  # Версия ОС
        'device' : user_agent_parse.device.family, # tablet desktop mobile
    }


def send_telegram_message(message: str):
    """
    Отправляет сообщение в Telegram через бота (синхронно).
    """
    url = f"https://api.telegram.org/bot{os.getenv('TG_TOKEN')}/sendMessage"
    payload = {
        "chat_id": os.getenv('TG_CHAT_ID'),
        "text": message,
    }
    response = requests.post(url, json=payload)
    return response.json()