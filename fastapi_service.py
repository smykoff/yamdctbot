from datetime import datetime
from os import getenv
from aiogram import Bot
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi import FastAPI, Request
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from pydantic import BaseModel
from yandex_music import Client

from db import get_session
from models import User


TG_TOKEN = getenv("TG_TOKEN")
YA_CLIENT_ID = getenv("YA_CLIENT_ID")

if not TG_TOKEN:
    raise Exception("TG_TOKEN not defined")

app = FastAPI()
bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    return templates.TemplateResponse("welcome.html", {"request": request, "bot_username": bot_username })

@app.get("/ya_redirect")
async def ya_redirect(request: Request):
    return templates.TemplateResponse("redirect.html", {"request": request })
  

class SaveUserTokenRequest(BaseModel):
    ya_token: str
    
    
@app.post("/save_user_token/{hash}")
async def save_user_token(request: SaveUserTokenRequest, hash: str):    
    try:
        Client(token=request.ya_token).init()
    except:
        return templates.TemplateResponse("error.html", {"request": request, "code": 422, "description": "Токен не подходит"})
    
    session = get_session()
    
    user = session.query(User).filter(User.login_hash == hash).first()

    if not user:
        return templates.TemplateResponse("error.html", {"request": request, "code": 404, "description": "Страница удалена или никогда не существовала"})
    
    if not user.login_expires_in or user.login_expires_in < datetime.now():
        return templates.TemplateResponse("error.html", {"request": request, "code": 419, "description": "Эта ссылка для входа истекла"})

    user.ya_token = request.ya_token
    user.login_hash = None
    user.login_expires_in = None
    session.commit()
    
    await bot.send_message(user.telegram_id, "Заебись, ты залогинился")
    
    return "Ok"


@app.get("/{login_hash}")
async def login(request: Request, login_hash: str):
    session = get_session()
    user = session.query(User).filter(User.login_hash == login_hash).first()
    
    if not user:
        return templates.TemplateResponse("error.html", {"request": request, "code": 404, "description": "Страница удалена или никогда не существовала"})
        
    if not user.login_expires_in or user.login_expires_in < datetime.now():
        return templates.TemplateResponse("error.html", {"request": request, "code": 419, "description": "Эта ссылка для входа истекла"})
    
    return templates.TemplateResponse("auth.html", {"request": request, "client_id": YA_CLIENT_ID })


async def start_fastapi():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8090,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()