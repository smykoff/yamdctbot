import asyncio
import logging
from os import getenv
import sys

from dotenv import load_dotenv
load_dotenv()

from aiogram_service import start_aiogram
from fastapi_service import start_fastapi

API_URL = getenv("API_URL")
YA_CLIENT_ID = getenv("YA_CLIENT_ID")

async def main() -> None:    
    tasks = [asyncio.create_task(start_aiogram())]
    
    if API_URL and YA_CLIENT_ID:
        tasks.append(asyncio.create_task(start_fastapi()))
    
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
