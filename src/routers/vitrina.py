import time
import datetime as dt
import aiofiles
from fastapi.responses import RedirectResponse
from sqlmodel import Field, SQLModel
from fastapi import BackgroundTasks, Depends, Response, status, Request, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.funcs import get_location, parse_user_agent


default_flow_id = '17671'

vitrina_router = APIRouter()

# Define a timezone with UTC+3 offset
utc_plus_3 = dt.timezone(dt.timedelta(hours=3))

class VitrinaClicks(SQLModel, table=True):
    __tablename__ = 'VitrinaClicks'
    
    id: int = Field(default=None, primary_key=True)
    user_ip: str | None
    country_code: str | None
    vitrina_name: str | None
    news_hash: str | None
    oneprofit_flow_id: str | None
    teaser_id: str | None
    site_id: str | None
    campaign_id: str | None
    click_id: str | None
    source_name: str | None
    block_id: str | None
    cpc: float | None
    category_id: str | None
    browser: str | None
    browser_version: str | None
    os: str | None = None
    os_version: str | None
    device: str | None
    city: str | None
    region: str | None
    created_at: dt.datetime = Field(default_factory=dt.datetime.now)

async def log_click_to_db(session: AsyncSession, headers: dict, query_params:dict, vitrina_name: str, news_hash: str):
    user_agent = headers.get('user-agent')
    user_ip = headers.get('x-real-ip')
    country_code, city, region = await get_location(user_ip)
    user_agent_parsed = parse_user_agent(user_agent)
    
    try:
        cpc = float(query_params.get('cpc'))
    except (TypeError, ValueError):
        cpc = 0  # Default value if parsing fails

    try:
        new_click = VitrinaClicks(
            user_ip=user_ip,
            country_code=country_code,
            vitrina_name=vitrina_name,
            news_hash=news_hash,
            oneprofit_flow_id=query_params.get('flow_id', default_flow_id),
            teaser_id=query_params.get('teaser_id'),
            site_id=query_params.get('site_id'),
            campaign_id=query_params.get('campaign_id'),
            click_id=query_params.get('click_id'),
            source_name=query_params.get('source_name'),
            block_id=query_params.get('block_id'),
            cpc=cpc,
            category_id=query_params.get('category_id'),
            browser=user_agent_parsed.get('browser'),
            browser_version=str(user_agent_parsed.get('browser_version')),
            os=user_agent_parsed.get('os'),
            os_version=str(user_agent_parsed.get('os_version')),
            device=user_agent_parsed.get('device'),
            city=city,
            region=region
        )
        session.add(new_click)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()  # Важно!




@vitrina_router.get('/vitrina/{vitrina_name}/{news_hash}')
async def click(
    request: Request,
    background_tasks: BackgroundTasks,
    vitrina_name: str,
    news_hash: str,
    session: AsyncSession = Depends(get_session),
):
    # Log the click in the background
    background_tasks.add_task(
        log_click_to_db,
        session,
        request.headers,
        request.query_params,
        vitrina_name,
        news_hash
    )

    # Get query parameters (with defaults)
    query_params = request.query_params
    site_id = query_params.get('site_id', '')
    teaser_id = query_params.get('teaser_id', '')
    campaign_id = query_params.get('campaign_id', '')
    cpc = query_params.get('cpc', '')
    click_id = query_params.get('click_id', '')
    source_name = query_params.get('source_name', '')
    flow_id = query_params.get('flow_id', default_flow_id)

    # Define redirect URL based on vitrina_name
    if vitrina_name == 'oneprofit':
        async with aiofiles.open('src/domain.txt', 'r') as file:
            domain = (await file.read()).strip()
        
        redirect_url = (
            f"https://{domain}/preview/new?utm_campaign={flow_id}&utm_content={news_hash}&utm_source={site_id}&utm_medium=2329&sid6={teaser_id}&sid7={campaign_id}&subid3={cpc}&subid4={click_id}&subid5={source_name}&is_visitor=1")
        
        if source_name == 'adprofex':
            redirect_url += f'&adp_click={click_id}'
    else:
        # Fallback URL or raise HTTPException if vitrina_name is invalid
        redirect_url = f"https://back.act-redir.space/back?utm_campaign={default_flow_id}&utm_source={site_id}&utm_medium=2329&sid6={teaser_id}&sid7={campaign_id}&subid3={cpc}&subid4={click_id}&subid5={source_name}"

    print(redirect_url)
    return RedirectResponse(redirect_url, status_code=307)
