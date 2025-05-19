import asyncio
import logging
import sys

from dotenv import load_dotenv
load_dotenv()

from aiogram_service import start_aiogram
from fastapi_service import start_fastapi

async def main() -> None:    
    bot_task = asyncio.create_task(start_aiogram())
    fastapi_task = asyncio.create_task(start_fastapi())
    
    await asyncio.gather(bot_task, fastapi_task)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
