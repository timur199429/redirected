import os
import httpx
import atexit
import requests

from user_agents import parse
from urllib.parse import urlparse

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

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


def get_domain(domain='red.skipnews.space'):
    url = 'https://' + domain + '?utm_campaign=999999&utm_content=56814b1d-40cf-40e7-8f49-d35685b2889e'
    try:
        response = requests.get(url, allow_redirects=True)
        parsed_url = urlparse(response.url)
        with open('domain.txt', 'w') as file:
            file.write(parsed_url.netloc)
        print('Domain updated')
    except requests.RequestException as e:
        print(f"Error processing URL: {e}")
        return None



def init_scheduler_domain(minutes:int=30):
    """Инициализация планировщика"""
    scheduler = BackgroundScheduler()
    scheduler.start()

    # Добавляем задачу в планировщик
    scheduler.add_job(
        func=get_domain,  # Функция, которую нужно выполнять
        trigger=IntervalTrigger(minutes=minutes),  # Интервал выполнения (каждые 30 минут)
        id="get_domain_job",  # Идентификатор задачи
        name="Update domain every 30 minutes",  # Имя задачи
        replace_existing=True,  # Заменить существующую задачу, если она уже есть
    )

    # Остановка планировщика при завершении приложения
    atexit.register(lambda: scheduler.shutdown())