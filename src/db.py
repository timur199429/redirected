import os
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv; load_dotenv()


# Create the database engine
URL_DATABASE = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# engine = create_engine(URL_DATABASE)
engine = create_async_engine(URL_DATABASE, echo=False)  # echo=True для логов

# Асинхронная фабрика сессий
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    # Создаем таблицы (асинхронно)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Генератор сессий для FastAPI Depends
async def get_session():
    async with async_session() as session:
        yield session

