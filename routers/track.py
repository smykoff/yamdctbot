import asyncio
import time
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, URLInputFile

from db import get_session
from models import User
from utlis.current_track import get_current_track

track_router = Router()


@track_router.message(Command('track'))
async def inline_handler(message: Message):
    if not message.from_user:
        await message.answer("Не знаю в чем проблема, надо админу писать")
        return

    session = get_session()
    user = session.query(User).filter(User.telegram_id == message.from_user.id).first()

    if not user or not user.ya_token:
        await message.answer("Залогиниться надо в боте")
        return
    
    async def send_wait_msg():
        await message.answer('Подожди, сейчас намутим')

    asyncio.create_task(send_wait_msg())
    
    track = await get_current_track(user.ya_token)
    
    if not track:        
        await message.answer("Трек не достается")
        return
    
    url = f"{track['download_link']}?nocache={time.time()}"
    input_file = URLInputFile(url, filename=f"{track['artist']} - {track['title']}.mp3")
    
    await message.answer_audio(
        audio=input_file,
        duration=track['duration'],
        title=track['title'],
        performer=track['artist'],
    )
