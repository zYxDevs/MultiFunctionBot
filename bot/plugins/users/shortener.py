import datetime
from re import search
from time import time

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from bot.config import *
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import ratelimit, user_commands
from bot.helpers.functions import forcesub, get_readable_time
from bot.logging import LOGGER
from bot.modules import shortener
from bot.modules.regex import URL_REGEX

commands = ["shorten", f"shorten@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
@ratelimit
async def shorten(client, message: Message):
    """
    Get AdFree Shortened URLs of your Link
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
    else:
        err = "<b><i>Please send a URL or reply to an URL to proceed!</i></b>"
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
    abc = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>"
    await message.reply_text(text=abc, disable_web_page_preview=True, quote=True)
    res1 = await shortener.bitly(url)
    res2 = await shortener.dagd(url)
    res3 = await shortener.tinyurl(url)
    res4 = await shortener.osdb(url)
    res5 = await shortener.ttm(url)
    res6 = await shortener.isgd(url)
    res7 = await shortener.vgd(url)
    res8 = await shortener.clickru(url)
    res9 = await shortener.clilp(url)
    time_taken = get_readable_time(time() - start)
    LOGGER(__name__).info(
        f" Destination : {res1} | {res2} | {res3} | {res4} | {res5} | {res6} | {res7} | {res8} | {res9}"
    )
    xyz = f"<u><b>Shortened URLs :\n\n</b></u>{res1}\n{res2}\n{res3}\n{res4}\n{res5}\n{res6}\n{res7}\n{res8}\n{res9}\n\n<b><i>NOTE:</i></b>\n<i>All the Shortened URLs redirect to the same URL as you entered and all of these links are Ad-Free.</i>\n\n<i>Time Taken : {time_taken}</i>"
    await message.reply_text(text=xyz, disable_web_page_preview=True, quote=True)
    try:
        msg = f"<b><i>User:</i></b> {user_}\n<b><i>User ID: </i></b><code>{user_id}</code>\n<i>User URL:</i> {url}\n<i>Destination URL:</i> {res1}\n{res2}\n{res3}\n{res4}\n{res5}\n{res6}\n{res7}\n{res8}\n{res9}\n\n<b><i>Time Taken:</i></b> {time_taken}"
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=msg,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except BaseException:
        pass
