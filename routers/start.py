from asyncio.log import logger
from datetime import datetime, timedelta
from os import getenv
import uuid
from aiogram import Router, html
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, LinkPreviewOptions

from db import get_session
from models import User

start_router = Router()

API_URL = getenv("API_URL")

@start_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if not API_URL:
        message.answer("Бот не настроен")
    
    if not message.from_user:
        logger.info("message.from_user is None")
        return
    
    session = get_session()
    user = session.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        user = User(
            telegram_id=message.from_user.id,
            login_hash = uuid.uuid4().hex,
            login_expires_in = datetime.now() + timedelta(minutes=30)
        )

        session.add(user)

    if user:
        user.login_hash = uuid.uuid4().hex
        user.login_expires_in = datetime.now() + timedelta(minutes=30)
        
    session.commit()
    
    await message.answer(f"Здарова, {html.bold(message.from_user.full_name)}")
    await message.answer(f"Чтобы начать пользоваться ботом, нужно {html.link("залогиниться", f"{API_URL}/{user.login_hash}")}.")
    await message.answer("После того, как ты залогинишься, можешь использовать написать @yamdctbot в любом чате и я покажу тебе, какой трек сейчас у тебя играет")
    await message.answer("Ну или просто напиши мне /track")


@start_router.message(Command('token'))
async def command_token_handler(message: Message) -> None:
   text = f"""Существует основные варианты получения токена:

- {html.link("Вебсайт", "https://music-yandex-bot.ru/")} (работает не для всех аккаунтов)
Яндекс.Браузеру отображает очень страшное предупреждение, т.к. сайт нарушает правила Яндекса

- Android приложение: {html.link("APK файл", "https://github.com/MarshalX/yandex-music-token/releases")}
- Расширение для {html.link("Google Chrome", "https://chrome.google.com/webstore/detail/yandex-music-token/lcbjeookjibfhjjopieifgjnhlegmkib")}
- Расширение для {html.link("Mozilla Firefox", "https://addons.mozilla.org/en-US/firefox/addon/yandex-music-token/ ")}

{html.quote("В приложении или расширениях ищите кнопку \"Скопировать токен\" в левом нижнем углу. В бота переходить не нужно.")}

Код каждого варианта открыт"""
   
   await message.answer(text, link_preview_options=LinkPreviewOptions(is_disabled=True))
