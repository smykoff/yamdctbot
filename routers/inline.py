from aiogram import Router, types
from aiogram.types import InlineQuery, InlineQueryResultAudio, InlineQueryResultArticle, InlineQueryResultUnion

from db import get_session
from models import User
from utlis.current_track import get_current_track
from utlis.search import search_tracks

inline_router = Router()


@inline_router.inline_query()
async def inline_handler(inline_query: InlineQuery):
    if not inline_query.from_user:
        error = create_error_result(description="Не знаю в чем проблема, надо админу писать", id="error-unknown")

        await inline_query.answer([error])
        return

    session = get_session()
    user = session.query(User).filter(User.telegram_id == inline_query.from_user.id).first()

    if not user or not user.ya_token:
        error = create_error_result(description="Залогиниться надо в боте", id="error-login")
        
        await inline_query.answer([error])
        return

    if inline_query.query:
        tracks = await search_tracks(user.ya_token, inline_query.query)
        
        if not tracks:
            error = create_error_result(description="Ищи чтонб попроще", id="no-tracks", title="Ничего не нашлось")
        
            await inline_query.answer([error])
            return
        
        results: list[InlineQueryResultUnion] = [InlineQueryResultAudio(
            id=f'{track['id']}',
            audio_url=track['download_link'],
            title=track['title'],
            performer=track['artist'],
        ) for track in tracks]
        
        await inline_query.answer(results)
        return
    
    track = await get_current_track(user.ya_token)

    if not track:
        error = create_error_result(description="Трек не достается", id="error-track-info")
        
        await inline_query.answer([error])
        return
    
    result = InlineQueryResultAudio(
        id=f'{track['id']}',
        audio_url=track['download_link'],
        title=track['title'],
        performer=track['artist'],
    )

    await inline_query.answer(results=[result], cache_time=1)


def create_error_result(description: str, id: str = "error", title = "Не работает, гуль", message_text = "Ничего нету"):
    return InlineQueryResultArticle(
        id=id,
        title=title,
        description=description,
        input_message_content=types.InputTextMessageContent(message_text=message_text),
    )