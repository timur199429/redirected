import time
from sqlmodel import SQLModel
from fastapi import BackgroundTasks, Response, status, Request, APIRouter




vitrina_router = APIRouter()


# class VitrinaClicks(SQLModel, table=True):
#     __tablename__ = 'VitrinaClicks'


# Функция для записи клика в базу (заглушка)
async def log_vitrina_click(request: Request, vitrina_name):
    time.sleep(2)  # Имитация долгой операции
    print(request.query_params)
    print(request.query_params.get('hello'))
    print("Click logged in the database")

@vitrina_router.get('/vitrina/{vitrina_name}')
async def click(request:Request, background_tasks: BackgroundTasks, vitrina_name):
    # Добавляем задачу в фоновый режим
    background_tasks.add_task(log_vitrina_click, request, vitrina_name)
    # Перенаправляем пользователя
    return Response(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": f"https://s3.timeweb.cloud/c327e49a-9cdc34a2-0262-4567-9cb2-736160213509/{vitrina_name}/index.html"})
