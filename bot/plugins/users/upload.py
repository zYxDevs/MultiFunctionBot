import datetime
import json
import os
import re
import subprocess
import time

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from bot.config import (
    BOT_USERNAME,
    DATABASE_URL,
    DEFAULT_UPLOAD_HOST,
    LOG_CHANNEL,
    UPLOAD_SIZE_LIMIT,
    prefixes,
)
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import ratelimit, user_commands
from bot.helpers.functions import forcesub, get_readable_file_size
from bot.helpers.pyro_progress import progress
from bot.logging import LOGGER

service_id_rx = re.compile("#(\d{1,2})")
tgUrlRx = re.compile("https://t\.me/c/(\d+)/(\d+)")

SERVICES = [
    "anonfiles",
    "catbox",
    "fileio",
    "filemail",
    "gofile",
    "krakenfiles",
    "letsupload",
    "megaup",
    "mixdrop",
    "pixeldrain",
    "racaty",
    "transfersh",
    "uguu",
    "wetransfer",
    "workupload",
    "zippyshare",
]

upload_usage = """**Supported Upload hosts:**`
+----+-------------+--------+
| #  |     Host    |  Limit |
+====+=============+========+
| 1  | anonfiles   | 20 GB  |
+----+-------------+--------+
| 2  | Catbox      | 200 MB |
+----+-------------+--------+
| 3  | file.io     | 2 GB   |
+----+-------------+--------+
| 4  | Filemail    | 5 GB   |
+----+-------------+--------+
| 5  | Gofile      | unlim  |
+----+-------------+--------+
| 6  | KrakenFiles | 1 GB   |
+----+-------------+--------+
| 7  | LetsUpload  | 10 GB  |
+----+-------------+--------+
| 8  | MegaUp      | 5 GB   |
+----+-------------+--------+
| 9  | MixDrop     | unlim  |
+----+-------------+--------+
| 10 | pixeldrain  | 10 GB  |
+----+-------------+--------+
| 11 | Racaty      | 10 GB  |
+----+-------------+--------+
| 12 | transfer.sh | unlim  |
+----+-------------+--------+
| 13 | Uguu        | 128 MB |
+----+-------------+--------+
| 14 | WeTransfer  | 2 GB   |
+----+-------------+--------+
| 15 | workupload  | 2 GB   |
+----+-------------+--------+
| 16 | zippyshare  | 500 MB |
+----+-------------+--------+`

**Supported links: TG file**
ex: TG file to WeTransfer:
reply to a file with `/upload #14`
"""


@Client.on_message(filters.command(["upload", f"upload@{BOT_USERNAME}"], **prefixes))
@user_commands
@ratelimit
async def thirdparty_upload(client, message: Message):
    """
    Upload TG Files to Third Party Services
    """
    fsub = await forcesub(client, message)
    if not fsub:
        return

    user_id = message.from_user.id
    uname = message.from_user.mention

    if DATABASE_URL is not None:
        if not await DatabaseHelper().is_user_exist(user_id):
            await DatabaseHelper().add_user(user_id)
            try:
                join_dt = await DatabaseHelper().get_bot_started_on(user_id)
                logmsg = f"<i>A New User has started the Bot: {message.from_user.mention}.</i>\n\n<b>Join Time</b>: {join_dt}"
                await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=logmsg,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Exception as err:
                LOGGER(__name__).error(f"BOT Log Channel Error: {err}")
        last_used_on = await DatabaseHelper().get_last_used_on(user_id)
        if last_used_on != datetime.date.today().isoformat():
            await DatabaseHelper().update_last_used_on(user_id)

    serviceID = service_id_rx.search(message.text)
    if serviceID:
        serviceID = int(serviceID.group(1)) - 1
        if serviceID > 15:
            await message.reply_text(
                "Sorry could not understand the host you wanted the file to be uploaded to!"
            )
            return
    else:
        serviceID = DEFAULT_UPLOAD_HOST

    msg = "<b><i>Please wait while I download your Telegram file...</i></b>"
    progressMessage = await message.reply_text(
        text=msg, disable_web_page_preview=True, quote=True
    )
    time.sleep(1)

    if message.reply_to_message or "t.me" in message.text:
        result = tgUrlRx.search(message.text)
        if result:
            chatid = "-100" + result.group(1)
            mid = result.group(2)
            msg = client.get_messages(chatid, int(mid))
        else:
            msg = message.reply_to_message
        mediaType = msg.media.value
        if mediaType == "video":
            media = msg.video
        elif mediaType == "audio":
            media = msg.audio
        elif mediaType == "document":
            media = msg.document
        else:
            await progressMessage.edit(text="This media type is not supported!")
            return

        fileName = media.file_name
        size = media.file_size

        limit = UPLOAD_SIZE_LIMIT * 1024**3
        if size > limit:
            await progressMessage.edit(
                text=f"Your File size is {get_readable_file_size(size)} and max allowed size is {UPLOAD_SIZE_LIMIT} GB!"
            )
            return

        file_path = os.path.join(os.getcwd(), "Downloads", fileName)
        if not os.path.exists(file_path):
            start_time = time.time()
            await progressMessage.edit(
                text=f"Downloading: `{fileName}`\n Size: {get_readable_file_size(size)}"
            )
            await msg.download(
                file_path,
                progress=progress,
                progress_args=(progressMessage, fileName, start_time),
            )

        file_name = os.path.basename(file_path)
        await progressMessage.edit(
            text=f"Uploading to {SERVICES[serviceID]}...\n`{file_name}` "
        )

        subprocess.Popen(
            [
                "./upload_module_x64",
                SERVICES[serviceID],
                "-f",
                file_path,
                "-j",
                "response.json",
            ]
        ).wait()

        response = json.load(open("response.json"))

        if not response["jobs"][-1]["ok"]:
            await progressMessage.delete()
            await message.reply_text(
                text=f"`{response['jobs'][-1]['error_text']}`\n<b>CC: </b>{uname} (ID: <code>{user_id}</code>)",
                disable_web_page_preview=True,
                quote=True,
            )
        else:
            await progressMessage.delete()
            await message.reply_text(
                text=f"<b>Name:</b> <i>{response['jobs'][-1]['filename']}</i>\n<b>Host:</b> <i>{SERVICES[serviceID]}</i>\n<b>URL:</b> {response['jobs'][-1]['url']}",
                disable_web_page_preview=True,
                quote=True,
            )

        try:
            os.remove(file_path)
        except Exception as e:
            LOGGER(__name__).warning(f"Could not delete File on Disk due to : {e}")

    else:
        await progressMessage.delete()
        await message.reply_text(
            text=upload_usage, disable_web_page_preview=True, quote=True
        )
