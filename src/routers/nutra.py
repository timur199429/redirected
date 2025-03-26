import asyncio
import datetime as dt
from sqlmodel import Field, SQLModel, Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import BackgroundTasks, Depends, Response, status, Request, APIRouter

from src.funcs import get_location, parse_user_agent, send_telegram_message
from src.db import get_session

nutra_router = APIRouter()

# Define a timezone with UTC+3 offset
utc_plus_3 = dt.timezone(dt.timedelta(hours=3))

class NutraClicks(SQLModel, table=True):
    __tablename__ = 'NutraClicks'
    
    id: int = Field(default=None, primary_key=True)
    user_ip: str | None
    country_code: str | None
    offer_category: str | None
    landing_name: str | None
    teaser_id: str | None
    site_id: str | None
    campaign_id: str | None
    click_id: str | None
    source_name: str | None
    block_id: str | None
    cpc: str | None
    category_id: str | None
    browser: str | None
    browser_version: str | None
    os: str | None
    os_version: str | None
    device: str | None
    city: str | None
    region: str | None
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(utc_plus_3))  # Add a timestamp


async def log_click_to_db(session: Session, headers: dict, query_params:dict, offer_category: str, landing_name: str):
    user_agent = headers.get('user-agent')
    user_ip = headers.get('x-real-ip')
    country_code, city, region = await get_location(user_ip)
    user_agent_parsed = parse_user_agent(user_agent)
    
    click = NutraClicks(
        user_ip=user_ip,
        country_code=country_code,
        offer_category=offer_category,
        landing_name=landing_name,
        teaser_id=query_params.get('teaser_id'),
        site_id=query_params.get('site_id'),
        campaign_id=query_params.get('campaign_id'),
        click_id=query_params.get('click_id'),
        source_name=query_params.get('source_name'),
        block_id=query_params.get('block_id'),
        cpc=query_params.get('cpc'),
        category_id=query_params.get('category_id'),
        browser=user_agent_parsed.get('browser'),
        browser_version=user_agent_parsed.get('browser_version'),
        os=user_agent_parsed.get('os'),
        os_version=user_agent_parsed.get('os_version'),
        device=user_agent_parsed.get('device'),
        city=city,
        region=region
    )

    
    session.add(click)
    session.commit()
    session.refresh(click)
    print("Click logged in the database")

@nutra_router.get("/nutra/{offer_category}/{landing_name}")
async def track_and_redirect(
    request: Request,
    background_tasks: BackgroundTasks,
    offer_category: str,
    landing_name: str,
    session: Session = Depends(get_session),
):
    # Добавляем задачу в фон (FastAPI сам запустит её асинхронно)
    background_tasks.add_task(
        log_click_to_db,
        session,
        request.headers,
        request.query_params,
        offer_category,
        landing_name
    )
    
    # Мгновенный редирект (без ожидания завершения log_click_to_db)
    redirect_url = f"https://bucket.act-redir.space/{offer_category}/{landing_name}/index.html?{request.query_params}&path={offer_category}{landing_name}"
    return RedirectResponse(redirect_url, status_code=307)  # 307 сохраняет метод запроса




@nutra_router.post("/submit-form/")
async def submit_form(request: Request):
    # Получаем все данные формы, включая скрытые поля
    form_data = await request.form()
    
    # # referer
    # referer_url = request.headers.get("Referer")
    
    # Извлекаем имя и телефон
    name = form_data.get("name")
    phone = form_data.get("phone")
    click_id = form_data.get("click_id")
    path = form_data.get("path")
    
    # Формируем сообщение для Telegram
    message = f"Новый лид!\nИмя: {name}\nТелефон: {phone}\nclick_id: {click_id}\nPath: {path}"
    
    # Отправляем сообщение в Telegram
    send_telegram_message(message)
    
    # Редирект на страницу успеха
    return RedirectResponse(url="/success", status_code=303)



@nutra_router.get('/success/')
async def success():
    # Открываем HTML-файл
    with open('src/success/index.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Возвращаем HTML-страницу
    return HTMLResponse(content=html_content)


