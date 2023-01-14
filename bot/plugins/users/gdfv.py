import datetime
from re import search
from time import sleep, time

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import ratelimit, user_commands
from bot.helpers.functions import forcesub, get_readable_time
from bot.logging import LOGGER
from bot.modules.gdrive_direct import *
from bot.modules.regex import *

commands = ["clone", f"clone@{BOT_USERNAME}", "gd", f"gd@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
@ratelimit
async def gd(client, message: Message):
    """
    Get GDrive Links for various Drive File Sharer
    """
    global res, time_taken
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
    msg_text = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Processing your URL.....</b>"
    msg = await message.reply_text(
        text=msg_text, disable_web_page_preview=True, quote=True
    )
    LOGGER(__name__).info(f" Received : {cmd} - {url}")
    sleep(1)
    is_gdtot = is_gdtot_link(url)
    is_drivehubs = is_drivehubs_link(url)
    is_unified = is_unified_link(url)
    is_udrive = is_udrive_link(url)
    is_sharer = is_sharer_link(url)
    is_sharedrive = is_sharedrive_link(url)
    is_filepress = is_filepress_link(url)
    if is_gdtot:
        link_type = "GDTot"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await gdtot(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Direct Gdrive Link :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif is_drivehubs:
        link_type = "DriveHubs"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await drivehubs(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Direct Gdrive Link :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif is_unified:
        link_type = "AppDrive LookAlike"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        # res = await unified(url)

        time_taken = get_readable_time(time() - start)
        # LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        # b = f"<b>Direct Gdrive Link :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        b = f"<b><i>AppDrive and its lookalikes have implemented Captcha.\n\nSo it would not work for now</i></b>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif is_udrive:
        link_type = "HubDrive LookAlike"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await udrive(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Direct Gdrive Link :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif is_sharer:
        link_type = "Sharerpw"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await sharerpw(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Direct Gdrive Link :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif is_sharedrive:
        link_type = "Sharedrive"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await shareDrive(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Direct Gdrive Link :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif is_filepress:
        link_type = "FilePress"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = filepress(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Direct Gdrive Link :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "pahe." in url:
        link_type = "Pahe"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await pahe(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Direct Gdrive Link :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "drive.google.com" in url:
        await msg.delete()
        err = "You have entered a Google Drive Link!"
        await message.reply_text(text=err, disable_web_page_preview=True, quote=True)
        return
    else:
        await msg.delete()
        err = "This Command does not support this Link!"
        await message.reply_text(text=err, disable_web_page_preview=True, quote=True)
        return
    try:
        logmsg = f"<b><i>User:</i></b> {user_}\n<b><i>User ID: </i></b><code>{user_id}</code>\n<i>User URL:</i> {url}\n<i>Command:</i> {cmd}\n<i>Destination URL:</i> {res}\n\n<b><i>Time Taken:</i></b> {time_taken}"
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=logmsg,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception as err:
        LOGGER(__name__).error(f"BOT Log Channel Error: {err}")
