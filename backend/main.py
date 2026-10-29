from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import SQLModel
from database import engine
import models
import os

# Import routers
from routers import (
    auth_router, service_router, requests_router, 
    inventory_router, admin_router, master_router, stats_router
)

app = FastAPI(title="Ремонтная Мастерская")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# --- FRONTEND CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
MEDIA_DIR = os.path.join(BASE_DIR, "backend", "media")

os.makedirs(MEDIA_DIR, exist_ok=True)

# Mount static files (CSS, JS)
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="static_js")
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=FRONTEND_DIR)

# --- API ROUTERS ---
app.include_router(auth_router.router)
app.include_router(service_router.router) # Note: matching your screenshot name
app.include_router(requests_router.router)
app.include_router(inventory_router.router)
app.include_router(admin_router.router)
app.include_router(master_router.router)
app.include_router(stats_router.router)

@app.get("/", response_class=HTMLResponse)
def serve_login(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/ui/client", response_class=HTMLResponse)
def serve_client(request: Request):
    return templates.TemplateResponse(request=request, name="client.html")

@app.get("/ui/master", response_class=HTMLResponse)
def serve_master(request: Request):
    return templates.TemplateResponse(request=request, name="master.html")

@app.get("/ui/admin", response_class=HTMLResponse)
def serve_admin(request: Request):
    return templates.TemplateResponse(request=request, name="admin.html")