# backend/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from database import engine
import models
import os

from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

# Import routers
from routers import auth_router, services_router, requests_router, inventory_router, admin_router, master_router,stats_router

app = FastAPI(title="Ремонтная Мастерская")
templates = Jinja2Templates(directory="templates") 

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

os.makedirs("static", exist_ok=True)
os.makedirs("media", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(auth_router.router)
app.include_router(services_router.router)
app.include_router(requests_router.router)
app.include_router(inventory_router.router)
app.include_router(admin_router.router)
app.include_router(master_router.router)
app.include_router(stats_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Repair Shop API!"}

@app.get("/ui", response_class=HTMLResponse)
def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})