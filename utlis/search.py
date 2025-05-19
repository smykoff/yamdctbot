import asyncio
from yandex_music import ClientAsync, Track

async def search_tracks(token: str, text: str):
  client = ClientAsync(token)
  await client.init()
  
  s = await client.search(text, type_='track')
  
  if not s or not s.tracks or not s.tracks.results:
    return
  
  # print(s.tracks.results[:10].__len__())
  
  # pprint.pprint(json.dumps(
  #   s.tracks.results
  # ), width=180)
  
  tracks = await asyncio.gather(
    *[format_track(track) for track in s.tracks.results[:4]]
  )
  
  # pprint.pprint(tracks)
  
  return tracks


async def format_track(track: Track):
  download_info, *_ = await track.get_download_info_async(get_direct_links=True)
  
  return {
    'id': track.id,
    'download_link': download_info.direct_link,
    'cover_link': f"https://{track.cover_uri[:-2]}1000x1000" if track.cover_uri else None,
    'duration': track.duration_ms // 1000 if track.duration_ms else None,
    'title': track.title,
    'artist': ", ".join(track.artists_name())
  }
