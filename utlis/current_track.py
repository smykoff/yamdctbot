import json
from os import getenv
import random
import string
import aiohttp

from ya_client import YandexMusicClient

YA_TOKEN = getenv('YA_TOKEN')

async def get_current_track(token: str):
  device_id = generate_device_id()

  ws_proto = {
    "Ynison-Device-Id": device_id,
    "Ynison-Device-Info": json.dumps({"app_name": "Chrome", "type": 1}),
  }

  data = await create_ynison_ws(token, ws_proto)

  ws_proto["Ynison-Redirect-Ticket"] = data["redirect_ticket"]

  payload = {
    "update_full_state": {
      "player_state": {
        "player_queue": {
          "current_playable_index": -1,
          "entity_id": "",
          "entity_type": "VARIOUS",
          "playable_list": [],
          "options": {"repeat_mode": "NONE"},
          "entity_context": "BASED_ON_ENTITY_BY_DEFAULT",
          "version": {"device_id": device_id, "version": 9021243204784341000, "timestamp_ms": 0},
          "from_optional": "",
        },
        "status": {
          "duration_ms": 0,
          "paused": True,
          "playback_speed": 1,
          "progress_ms": 0,
          "version": {"device_id": device_id, "version": 8321822175199937000, "timestamp_ms": 0},
        },
      },
      "device": {
        "capabilities": {"can_be_player": True, "can_be_remote_controller": False, "volume_granularity": 16},
        "info": {
          "device_id": device_id,
          "type": "WEB",
          "title": "Chrome Browser",
          "app_name": "Chrome",
        },
        "volume_info": {"volume": 0},
        "is_shadow": True,
      },
      "is_currently_active": False,
    },
    "rid": "ac281c26-a047-4419-ad00-e4fbfda1cba3",
    "player_action_timestamp_ms": 0,
    "activity_interception_type": "DO_NOT_INTERCEPT_BY_DEFAULT",
  }

  async with aiohttp.ClientSession() as session:
    async with session.ws_connect(
      f"wss://{data['host']}/ynison_state.YnisonStateService/PutYnisonState",
      headers={
        "Sec-WebSocket-Protocol": f"Bearer, v2, {json.dumps(ws_proto)}",
        "Origin": "http://music.yandex.ru",
        "Authorization": f"OAuth {token}",
      }
    ) as ws:
      await ws.send_str(json.dumps(payload))
      response = await ws.receive()
      ynison = json.loads(response.data)
      
  track = ynison["player_state"]["player_queue"]["playable_list"][
    ynison["player_state"]["player_queue"]["current_playable_index"]
  ]
  
  return await get_track_by_id(token, track["playable_id"])
  

def generate_device_id(length: int = 16) -> str:
  return ''.join(random.choices(string.ascii_lowercase, k=length))


async def create_ynison_ws(ya_token: str, ws_proto: dict) -> dict:
  async with aiohttp.ClientSession() as session:
    async with session.ws_connect(
      "wss://ynison.music.yandex.ru/redirector.YnisonRedirectService/GetRedirectToYnison",
      headers={
        "Sec-WebSocket-Protocol": f"Bearer, v2, {json.dumps(ws_proto)}",
        "Origin": "http://music.yandex.ru",
        "Authorization": f"OAuth {ya_token}",
      },
    ) as ws:
      response = await ws.receive()
      return json.loads(response.data)


async def get_track_by_id(token, track_id: int):
  if YA_TOKEN:
    token = YA_TOKEN
  
  async with YandexMusicClient(token) as client:
    try:
      track, *_ = await client.tracks(track_id)    
      download_info, *_ = await track.get_download_info_async(get_direct_links=True)
      
      return {
        'id': track_id,
        'download_link': download_info.direct_link,
        'cover_link': f"https://{track.cover_uri[:-2]}1000x1000" if track.cover_uri else None,
        'duration': track.duration_ms // 1000 if track.duration_ms else None,
        'title': track.title,
        'artist': ", ".join(track.artists_name())
      }

    except Exception as e:
      raise Exception("Track information could not be retrieved")