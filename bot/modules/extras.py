import json
import re

import requests

from bot.helpers.functions import url_exists
from bot.modules.pasting import telegraph_paste


async def headfone(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    rslt = f"<b>User URL :</b> <code>{url}</code><br>"
    client = requests.Session()
    resp = client.get(url)
    raw_json = re.search("tracks = (.+);", resp.text).group(1)
    name = re.search("<div class=channel-info-title> (.+?) </div>", resp.text).group(1)
    rslt += f"<i>Channel Name :</i> <b>{name}</b><br>"
    json_data = json.loads(raw_json)
    num = 1
    cdn = re.search("https://(.+?).cloudfront.net", json_data[0]["url"]).group(1)
    for audio in json_data:
        title = f"{str(num).zfill(2)}. {audio['title']}.m4a"
        num += 1
        url = audio["url"]
        if "cdn" in url:
            url = url.replace("cdn", cdn)
        rslt += f"• <b>{title}</b> - <code>{url}</code><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def hungama(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    idRegx = re.compile(r"/(\d+)")
    metadataRegx = re.compile(r"videodt = ({[\s\S]+?};)")
    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
    }
    params = {
        "c": "common",
        "m": "get_video_mdn_url",
    }
    rslt = f"<b>User URL :</b> <code>{url}</code><br>"
    client = requests.Session()
    id = idRegx.search(url).group(1)
    resp = requests.get(f"https://www.hungama.com/video/_/{id}/")
    metadata = metadataRegx.search(resp.text).group(1)[:-1]
    metadata = json.loads(metadata)
    name = f"{metadata['singer_list']} - {metadata['video_name']} ({metadata['release_date'][:4]}).mp4"
    rslt += f"<i>File Name :</i> <b>{name}</b><br>"
    data = f"content_id={id}"
    resp2 = client.post(
        "https://www.hungama.com/index.php", params=params, headers=headers, data=data
    )
    if "media.hungama." not in resp2.text:
        return "Error while trying to download from Hungama!"
    f_url = resp2.json()["stream_url"]
    rslt += f"<b>Download URL :</b> <code>{f_url}</code><br>"
    rslt += f"<br><b><u>Metadata: </u></b><br>"
    if metadata["album_name"] != "":
        rslt += f"<b>Album Name:</b> <i>{metadata['album_name']}</i><br>"
    if metadata["genre"] != "":
        rslt += f"<b>Genre:</b> <i>{metadata['genre']}</i><br>"
    if metadata["language"] != "":
        rslt += f"<b>Language:</b> <i>{bytes(metadata['language'], 'UTF-8')}</i><br>"
    if metadata["vendor"] != "":
        rslt += f"<b>Vendor:</b> <i>{metadata['vendor']}</i><br>"
    if metadata["singer_list"] != "":
        rslt += f"<b>Singers List:</b> <i>{metadata['singer_list']}</i><br>"
    if metadata["artist"] != "":
        rslt += f"<b>Artist:</b> <i>{metadata['artist']}</i><br>"
    if metadata["release_date"] != "":
        rslt += f"<b>Release Date:</b> <i>{bytes(metadata['release_date'][:4] + '-' + metadata['release_date'][4:6] + '-' + metadata['release_date'][6:], 'UTF-8')}</i><br>"
    if metadata["musicdirector_list"] != "":
        rslt += f"<b>Music Directors:</b> <i>{bytes(metadata['musicdirector_list'], 'UTF-8')}</i><br>"
    if metadata["actor_list"] != "":
        rslt += (
            f"<b>Actors List:</b> <i>{bytes(metadata['actor_list'], 'UTF-8')}</i><br>"
        )
    if metadata["lyricist_list"] != "":
        rslt += f"<b>Lyricists List:</b> <i>{bytes(metadata['lyricist_list'], 'UTF-8')}</i><br>"
    if metadata["image_path"] != "":
        rslt += f"<b>Image:</b> <i>{metadata['image_path']}</i><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url
