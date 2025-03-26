import time
import datetime as dt
from sqlmodel import Field, SQLModel, Session
from fastapi import BackgroundTasks, Depends, Response, status, Request, APIRouter

from src.db import get_session
from src.funcs import get_location, parse_user_agent




vitrina_router = APIRouter()

# Define a timezone with UTC+3 offset
utc_plus_3 = dt.timezone(dt.timedelta(hours=3))

class VitrinaClicks(SQLModel, table=True):
    __tablename__ = 'VitrinaClicks'
    
    id: int = Field(default=None, primary_key=True)
    user_ip: str | None = None
    country_code: str | None = None
    vitrina_name: str | None = None
    news_hash: str | None = None
    oneprofit_flow_id: str | None = None
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

async def log_vitrina_click(session: Session, headers: dict, query_params:dict, vitrina_name: str, news_hash: str):
    user_agent = headers.get('user-agent')
    user_ip = headers.get('x-real-ip')
    country_code, city, region = await get_location(user_ip)
    user_agent_parsed = parse_user_agent(user_agent)
    
    click = VitrinaClicks(
        user_ip=user_ip,
        country_code=country_code,
        vitrina_name=vitrina_name,
        news_hash=news_hash,
        oneprofit_flow_id=query_params.get('flow_id'),
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



@vitrina_router.get('/vitrina/{vitrina_name}/{news_hash}')
async def click(request:Request, background_tasks: BackgroundTasks, vitrina_name, news_hash, session: Session = Depends(get_session)):
    # Проверяем, была ли кука "processed" установлена
    if "processed" not in request.cookies:
        # Добавляем задачу в фоновый режим
        background_tasks.add_task(
            log_vitrina_click, session, request.headers, request.query_params, vitrina_name, news_hash
        )
    
    # Собираем query_params для передачи в URL редиректа
    query_params = request.query_params
    site_id = query_params.get('site_id')
    teaser_id = query_params.get('teaser_id')
    campaign_id = query_params.get('campaign_id')
    cpc = query_params.get('cpc')
    click_id = query_params.get('click_id')
    source_name = query_params.get('source_name')
    flow_id = query_params.get('flow_id')
    
    if vitrina_name == 'oneprofit':
        with open('domain.txt','r') as file:
            domain = file.read().strip()
            redirect_url = f"https://{domain}/preview/new?utm_campaign={flow_id}&utm_content={news_hash}&utm_source={site_id}&utm_medium=2329&sid6={teaser_id}&sid7={campaign_id}&subid3={cpc}&subid4={click_id}&subid5={source_name}&is_visitor=1"
            if source_name == 'adprofex':
                redirect_url += f'&adp_click={click_id}'

    print(redirect_url)

    # https://pump-lighttight.com/preview/new?utm_campaign=75034&utm_content=f0fdd327-d374-46b2-981b-975c5e2d50b6&utm_source=[SID]&utm_medium=2329&sid6=[TID]&sid7=[CAMPAIGN]&subid3=[CPCP]&subid4=[CLICK_ID]&subid5=adprofex&is_visitor=1&adp_click=[CLICK_ID]

    # https://pump-lighttight.com/preview/new?utm_campaign=76406&utm_content=484146b9-f61c-448d-bf4a-384a35825ae1&utm_source=None&utm_medium=2329&sid6=None&sid7=None&subid3=None&subid4=None&subid5=None&is_visitor=1

    # Перенаправляем пользователя
    response = Response(
        status_code=status.HTTP_303_SEE_OTHER,
        headers={"Location": redirect_url}
    )

    # Устанавливаем куку, чтобы избежать повторной обработки
    response.set_cookie(key="processed", value="true", max_age=5)  # Кука действует 60 секунд

    return response
