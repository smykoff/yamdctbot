from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.bot import Bot as BotClass
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from routers.inline import inline_router
from routers.login import login_router
from routers.start import start_router
from routers.track import track_router

from db import get_session


def on_shutdown():
    get_session().close()
    
async def on_startup(bot: BotClass):
    commands = [
        BotCommand(command="/start", description="Начало работы"),
        BotCommand(command="/track", description="Текущий трек"),
        
        BotCommand(command="/token", description="Узнать как получить токен"),
        BotCommand(command="/login", description="Установить токен вручную"),
        BotCommand(command="/unlogin", description="Удалить токен"),
    ]
    
    await bot.set_my_commands(commands)


async def start_aiogram() -> None:
    TG_TOKEN = getenv("TG_TOKEN")

    if not TG_TOKEN:
        raise Exception("TG_TOKEN not defined")
    
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(inline_router)
    dp.include_router(login_router)
    dp.include_router(start_router)
    dp.include_router(track_router)

    bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)