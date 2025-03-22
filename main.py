from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import main_router
from db import db_init

@asynccontextmanager
async def lifespan(app: FastAPI):    
    print("Server is starting...")
    db_init()
    yield
    print("server is stopping")

app = FastAPI()
app.include_router(main_router)
# Монтируем папку со статическими файлами
app.mount("/success", StaticFiles(directory="success"), name="success")




# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run('main:app', port=8000, reload=True)