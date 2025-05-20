import os
from dotenv import load_dotenv
from yandex_music import ClientAsync
from yandex_music.utils.request_async import Request

load_dotenv()

PROXY_URL = os.getenv("PROXY_URL")


class YandexMusicClient:
  def __init__(self, token: str):
    self.client: ClientAsync | None = None
    self.token: str = token

  async def __aenter__(self) -> ClientAsync:
    if PROXY_URL:
      proxied_request = Request(proxy_url=PROXY_URL)
      self.client = ClientAsync(self.token, request=proxied_request)
      
    else:
      self.client = ClientAsync(self.token)

    await self.client.init()

    return self.client

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    pass
