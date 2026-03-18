from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import Base, engine
from models import RefreshToken, Task, User  # noqa: F401
from routers.router_auth import router as router_auth
from routers.router_task import router as router_task
from routers.router_user import router as router_user

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router_task)
app.include_router(router_user)
app.include_router(router_auth)

Base.metadata.create_all(bind=engine)

# Ruta raíz - redirige al login
@app.get("/")
async def root():
    return FileResponse("static/login.html")