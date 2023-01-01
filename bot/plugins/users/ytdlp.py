import datetime
from re import search
from time import time

from pyrogram import Client, enums, filters
from pyrogram.types import Message
from yt_dlp import DownloadError, YoutubeDL
from yt_dlp.utils import (
    ContentTooShortError,
    ExtractorError,
    GeoRestrictedError,
    MaxDownloadsReached,
    PostProcessingError,
    UnavailableVideoError,
    XAttrMetadataError,
)

from bot.config import *
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import ratelimit, user_commands
from bot.helpers.functions import forcesub, get_readable_time
from bot.logging import LOGGER
from bot.modules.pasting import telegraph_paste
from bot.modules.regex import URL_REGEX, is_a_url

commands = ["ytdl", f"ytdl@{BOT_USERNAME}", "ytdlp", f"ytdlp@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
@ratelimit
async def ytdlp(client, message: Message):
    """
    Extract DL Links using YT-DLP
    """
    fsub = await forcesub(client, message)
    if not fsub:
        return
    msg_arg = message.text.replace("  ", " ")
    msg_args = msg_arg.split(" ", maxsplit=1)
    reply_to = message.reply_to_message
    global url, cmd
    if len(msg_args) > 1:
        if len(message.command) != 2:
            await message.reply_text("Sorry, Could not understand your Input!")
            return
        cmd = msg_args[0]
        url = msg_args[1]
    elif reply_to is not None:
        try:
            reply_text = search(URL_REGEX, reply_to.text)[0]
        except BaseException:
            reply_text = (
                search(URL_REGEX, reply_to.caption.markdown)[0]
                .replace("\\", "")
                .split("*")[0]
            )
        url = reply_text.strip()
        cmd = msg_args[0]
    elif message.command == (0 or 1) or reply_to is None:
        err = "<b><i>Please send a URL or reply to an URL to proceed!</i></b>"
        await message.reply_text(text=err, disable_web_page_preview=True, quote=True)
        return

    valid_url = is_a_url(url)
    if valid_url is not True:
        err = "<b><i>You did not seem to have entered a valid URL!</i></b>"
        await message.reply_text(text=err, disable_web_page_preview=True, quote=True)
        return

    uname = message.from_user.mention
    uid = f"<code>{message.from_user.id}</code>"
    user_id = message.from_user.id
    if message.from_user.username:
        user_ = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.username}</a>'
    else:
        user_ = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'

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

    start = time()
    LOGGER(__name__).info(f" Received : {cmd} - {url}")
    abc = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>YT-DLP Scraping</i>"
    init_msg = await message.reply_text(
        text=abc, disable_web_page_preview=True, quote=True
    )

    ydl_opts = {
        "addmetadata": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
    }

    ytdl_data = None
    errmsg = None
    try:
        with YoutubeDL(ydl_opts) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=False)
    except DownloadError as DE:
        errmsg = f"`{DE}`"
    except ContentTooShortError:
        errmsg = "`The download content was too short.`"
    except GeoRestrictedError:
        errmsg = "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`"
    except MaxDownloadsReached:
        errmsg = "`Max-downloads limit has been reached.`"
    except PostProcessingError:
        errmsg = "`There was an error during post processing.`"
    except UnavailableVideoError:
        errmsg = "`Media is not available in the requested format.`"
    except XAttrMetadataError as XAME:
        errmsg = f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`"
    except ExtractorError:
        errmsg = "`There was an error during info extraction.`"
    except Exception as e:
        errmsg = f"**Error : **\n__{e}__"

    if errmsg is not None:
        await init_msg.delete()
        await message.reply_text(text=errmsg, disable_web_page_preview=True, quote=True)
        return

    try:
        res = f"<b>Title:</b> <i>{ytdl_data['title']}</i><br>"
        res += "<b><i>DL Links:</i></b><br>"
        formats = ytdl_data.get("requested_formats") or [ytdl_data]
        for f in formats:
            res += f"• <code>{f['url']}</code><br>"
        tlg_url = await telegraph_paste(res)
    except Exception as e:
        await init_msg.delete()
        err = f"YT-DLP Engine could not process your URL!\nERROR: {e}"
        await message.reply_text(text=err, disable_web_page_preview=True, quote=True)
        return

    time_taken = get_readable_time(time() - start)
    LOGGER(__name__).info(f" Destination : {cmd} - {tlg_url}")
    xyz = f"<b>YT-DLP Result :\n</b>{tlg_url}\n\n<i>Time Taken : {time_taken}</i>"
    await message.reply_text(text=xyz, disable_web_page_preview=True, quote=True)
    try:
        logmsg = f"<b><i>User:</i></b> {user_}\n<b><i>User ID: </i></b><code>{user_id}</code>\n<i>User URL:</i> {url}\n<i>Command:</i> {cmd}\n<i>Destination URL:</i> {tlg_url}\n\n<b><i>Time Taken:</i></b> {time_taken}"
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=logmsg,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception as err:
        LOGGER(__name__).error(f"BOT Log Channel Error: {err}")
