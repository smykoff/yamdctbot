from asyncio.log import logger
from yandex_music import Client

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from models import User

from db import get_session

login_router = Router()

yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text="Да"),
        KeyboardButton(text="Нет")
    ]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


class LoginStates(StatesGroup):
    is_update_token = State()
    waiting_for_token = State()

@login_router.message(Command('unlogin'))
async def command_unlogin(message: Message):
    if not message.from_user:
        logger.info('message.from_user is None')
        return

    session = get_session()
    user = session.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if user:
        session.delete(user)
        session.commit()
        await message.answer('Ну все, ты разлогинился')
        return

    await message.answer('Ну ты и так не залогинен, че пытаться то?')

@login_router.message(Command('login'))
async def command_login_handler(message: Message, state: FSMContext):
    if not message.from_user:
        logger.info('message.from_user is None')
        return

    session = get_session()
    user = session.query(User).filter(User.telegram_id == message.from_user.id).first()

    if user:
        await state.set_state(LoginStates.is_update_token)
        await message.answer('Токен уже установлен')
        await message.answer('Хочешь обновить токен?', reply_markup=yes_no_kb)
        return

    await state.set_state(LoginStates.waiting_for_token)
    await message.answer('Отправь токен Я.Музыки в следующем сообщении')

@login_router.message(LoginStates.is_update_token)
async def command_answer_update_token(message: Message, state: FSMContext):
    if message.text == 'Да':
        await state.set_state(LoginStates.waiting_for_token)
        await message.answer('Отправь токен Я.Музыки в следующем сообщении')
        return
    
    await message.answer('Окей, оставим все как есть')
    await state.clear()

@login_router.message(LoginStates.waiting_for_token)
async def token_received(message: Message, state: FSMContext):
    if not message.from_user:
        logger.info("message.from_user is None")
        return
    
    if not message.text:
        await message.answer('Текстом токен, але')
        await message.answer('Давай по новой')    
        await state.clear()
        return

    try:
        Client(token=message.text).init()
    except:
        await message.answer('Этот токен не катит')
        await message.answer('Давай по новой')    
        await state.clear()
        return

    session = get_session()
    user = session.query(User).filter(User.telegram_id == message.from_user.id).first()

    if user:
        user.ya_token = message.text

    else:
        user = User(
            telegram_id=message.from_user.id,
            ya_token=message.text
        )

        session.add(user)
    
    session.commit()

    await message.answer(f'Заебись, токен я сохранил, теперь можно пользоваться ботом')
    await state.clear()