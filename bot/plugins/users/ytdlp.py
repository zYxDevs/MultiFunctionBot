import datetime
from re import search
from time import time

import yt_dlp
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from bot.config import *
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import user_commands
from bot.helpers.functions import forcesub, get_readable_time
from bot.logging import LOGGER
from bot.modules.pasting import telegraph_paste
from bot.modules.regex import URL_REGEX, is_a_url

prefixes = COMMAND_PREFIXES
commands = ["ytdl", f"ytdl@{BOT_USERNAME}", "ytdlp", f"ytdlp@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
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
    await message.reply_text(text=abc, disable_web_page_preview=True, quote=True)

    yt_info = yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}).extract_info(
        url, download=False
    )

    try:
        res = f"<b>Title:</b> <i>{yt_info['title']}</i><br>"
        res += "<b><i>DL Links:</i></b><br>"
        formats = yt_info.get("requested_formats") or [yt_info]
        for f in formats:
            res += f"• <code>{f['url']}</code><br>"
        tlg_url = await telegraph_paste(res)
    except Exception as e:
        tlg_url = f"YT-DLP Engine could not process your URL!\nERROR: {e}"

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