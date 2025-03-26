from sqlmodel import SQLModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

from src.db import get_session
clickback = APIRouter()

class ClickbackOneprofit(SQLModel, table=True):
    __tablename__ = 'clickback_oneprofit'

    id: int = Field(default=None, primary_key=True)
    amount: float
    site_id: str
    teaser_id: str
    campaign_id: str
    cpc: float
    click_id: str
    source_name: str
    created_at: str
    order_id: str

@clickback.get('/clickback/oneprofit')
async def oneprofit(request: Request, session:AsyncSession=Depends(get_session)):
    
    params = request.query_params
    amount = float(params.get('amount',0))
    site_id = params.get('stream','')
    teaser_id = params.get('subid1','')
    campaign_id = params.get('subid2','')
    cpc = float(params.get('subid3',0))
    click_id = params.get('subid4','')
    source_name = params.get('subid5','')
    created_at = params.get('created_at','')
    order_id = params.get('order_id','')

    try:
        new_click = ClickbackOneprofit(amount=amount,
                                    site_id=site_id,
                                    teaser_id=teaser_id,
                                    campaign_id=campaign_id,
                                    cpc=cpc,
                                    click_id=click_id,
                                    source_name=source_name,
                                    created_at=created_at,
                                    order_id=order_id)
        session.add(new_click)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()  # Важно!

