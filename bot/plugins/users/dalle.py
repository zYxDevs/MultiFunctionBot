import base64
import json
import os
import shutil

from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, Message

from bot.config import *
from bot.helpers.decorators import ratelimit, user_commands
from bot.helpers.functions import forcesub

commands = ["dalle", f"dalle@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
@ratelimit
async def dalle(client, message: Message):
    """
    DALL·E Mini - Generate images from a text prompt
    """
    global query

    fsub = await forcesub(client, message)
    if not fsub:
        return

    reply_to = message.reply_to_message

    if len(message.command) > 1:
        query = message.text.split("/dalle ")[1]
    elif reply_to is not None:
        query = reply_to.text
    elif len(message.command) < 2 or reply_to is None:
        err = "<b><i>Please send a query or reply to an query to proceed!</i></b>"
        await message.reply_text(text=err, disable_web_page_preview=True, quote=True)
        return

    try:
        await generateimages(client, message, query)
    except BaseException:
        e = "<b>Error encountered while generating Image from DALLE-Mini</b>"
        await message.reply_text(text=e, disable_web_page_preview=True, quote=True)
        return


reqUrl = "https://backend.craiyon.com/generate"
headersList = {
    "authority": "backend.craiyon.com",
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://www.craiyon.com",
    "pragma": "no-cache",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Linux",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
}


async def generateimages(client, message, query):

    payload = json.dumps({"prompt": query})
    response = requests.request(
        "POST", reqUrl, data=payload, headers=headersList
    ).json()
    os.mkdir(str(message.id))

    i = 1
    for ele in response["images"]:
        image = base64.b64decode(ele.replace("\\n", ""))
        with open(f"{message.id}/{i}.jpeg", "wb") as file:
            file.write(image)
        i = i + 1

    await client.send_media_group(
        chat_id=message.chat.id,
        media=[
            InputMediaPhoto(f"{message.id}/1.jpeg", caption=query),
            InputMediaPhoto(f"{message.id}/2.jpeg", caption=query),
            InputMediaPhoto(f"{message.id}/3.jpeg", caption=query),
            InputMediaPhoto(f"{message.id}/4.jpeg", caption=query),
            InputMediaPhoto(f"{message.id}/5.jpeg", caption=query),
            InputMediaPhoto(f"{message.id}/6.jpeg", caption=query),
            InputMediaPhoto(f"{message.id}/7.jpeg", caption=query),
            InputMediaPhoto(f"{message.id}/8.jpeg", caption=query),
            InputMediaPhoto(f"{message.id}/9.jpeg", caption=query),
        ],
    )

    shutil.make_archive(query, "zip", str(message.id))
    await client.send_document(
        chat_id=message.chat.id,
        document=f"{query}.zip",
        caption=f"{query}\n\n(Archive for Uncompressed Images)",
    )
    os.remove(f"{query}.zip")
    shutil.rmtree(str(message.id))
