import asyncio
import datetime as dt
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Field, SQLModel, Session
from fastapi import BackgroundTasks, Depends, Response, status, Request, APIRouter
from funcs import get_location, parse_user_agent, send_telegram_message
from db import get_session

nutra_router = APIRouter()

# Define a timezone with UTC+3 offset
utc_plus_3 = dt.timezone(dt.timedelta(hours=3))

class NutraClicks(SQLModel, table=True):
    __tablename__ = 'NutraClicks'
    
    id: int = Field(default=None, primary_key=True)
    user_ip: str | None = None
    country_code: str | None = None
    offer_category: str | None = None
    landing_name: str | None = None
    teaser_id: str | None = None #
    site_id: str | None = None #
    campaign_id: str | None = None #
    click_id: str | None = None #
    source_name: str | None = None #
    block_id: str | None = None #
    cpc: str | None = None #
    category_id: str | None = None #
    browser: str | None = None
    browser_version: str | None = None
    os: str | None = None
    os_version: str | None = None
    device: str | None = None
    city: str | None = None
    region: str | None = None
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(utc_plus_3))  # Add a timestamp


async def log_nutra_click(session: Session, headers: dict, query_params:dict, offer_category: str, landing_name: str):
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
async def click(
    request: Request,
    background_tasks: BackgroundTasks,
    offer_category: str,
    landing_name: str,
    session: Session = Depends(get_session),
):
    # Проверяем, была ли кука "processed" установлена
    if "processed" not in request.cookies:
        # Добавляем задачу в фоновый режим
        background_tasks.add_task(
            log_nutra_click, session, request.headers, request.query_params, offer_category, landing_name
        )

    # Собираем query_params для передачи в URL редиректа
    query_params = request.query_params
    redirect_url = f"https://bucket.act-redir.space/{offer_category}/{landing_name}/index.html?{query_params}&path={offer_category}{landing_name}"

    # Перенаправляем пользователя
    response = Response(
        status_code=status.HTTP_303_SEE_OTHER,
        headers={"Location": redirect_url}
    )

    # Устанавливаем куку, чтобы избежать повторной обработки
    response.set_cookie(key="processed", value="true", max_age=5)  # Кука действует 60 секунд

    return response




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
    with open('success/index.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Возвращаем HTML-страницу
    return HTMLResponse(content=html_content)


