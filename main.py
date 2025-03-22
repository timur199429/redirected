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

app = FastAPI(lifespan=lifespan)
app.include_router(main_router)
# Монтируем папку со статическими файлами
app.mount("/success", StaticFiles(directory="success"), name="success")




if __name__ == "__main__":
    port = 3478
    app.run(debug=True,host='0.0.0.0',port=port)