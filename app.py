from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.funcs import get_domain, init_scheduler_domain
from src.routers import main_router
from src.db import db_init

@asynccontextmanager
async def lifespan(app: FastAPI):    
    print("Server is starting...")
    db_init()
    get_domain()
    init_scheduler_domain()
    yield
    print("server is stopping")


app = FastAPI(lifespan=lifespan)
app.include_router(main_router)
# Монтируем папку со статическими файлами
app.mount("/success", StaticFiles(directory="src/success"), name="success")

@app.get('/')
async def index():
    return {'message':'ok'}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=3478)