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
from bot.modules import direct_link
from bot.modules.lists import *
from bot.modules.pasting import telegraph_paste
from bot.modules.regex import *

commands = ["direct", f"direct@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
@ratelimit
async def direct(client, message: Message):
    """
    Get Direct Link for various Supported URLs
    """
    global res, res2, time_taken
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
        err2 = "<b><i>You did not seem to have entered a valid URL!</i></b>"
        await message.reply_text(text=err2, disable_web_page_preview=True, quote=True)
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

    if DATABASE_URL is not None:
        if await DatabaseHelper().is_dblink_exist(url):
            a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>"
            await msg.edit(text=a)
            last_used_on = await DatabaseHelper().get_last_fetched_on(url)
            if last_used_on != datetime.date.today().isoformat():
                await DatabaseHelper().update_last_fetched_on(url)
            result = await DatabaseHelper().fetch_dblink_result(url)
            add_date = await DatabaseHelper().fetch_dblink_added(url)
            time_taken = get_readable_time(time() - start)
            LOGGER(__name__).info(f"Successfully Generated DL - DB:True - {result}")
            b = f"<b>Download Link :\n</b>{result}\n\n<i>Time Taken : {time_taken}</i>\n<i>Result Added on:</i>{add_date}"
            await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
            try:
                logmsg = f"<b><i>User:</i></b> {user_}\n<b><i>User ID:</i></b><code>{user_id}</code>\n<i>User URL:</i> {url}\n<i>Command:</i> {cmd}\n<i>Destination URL:</i> {result}\n\n<b><i>Time Taken:</i></b> {time_taken}\n\n<i>Result Added on:</i> {add_date}"
                await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=logmsg,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Exception as err:
                LOGGER(__name__).error(f"BOT Log Channel Error: {err}")
            return

    is_artstation = is_artstation_link(url)
    is_fichier = is_fichier_link(url)
    if is_artstation:
        link_type = "ArtStation"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.artstation(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "mdisk.me" in url:
        link_type = "MDisk"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.mdisk(url)
        res2 = await direct_link.mdisk_mpd(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b><i>Download Link: {res}\n MPD Link: {res2}</i></b>\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "wetransfer." in url or "we.tl" in url:
        link_type = "WeTransfer"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.wetransfer(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "gdbot." in url:
        link_type = "GDBot"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.gdbot(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "terabox." in url:
        link_type = "TeraBox"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.terabox(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link/s is/are :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "gofile." in url:
        link_type = "GoFile"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        # res = await direct_link.gofile(url)
        res = url  # Temporary Solution
        """ sleep(1)
        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>" """
        b = f"<b><i>Sorry! GoFile Bypass is not supported anymore</i></b>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "megaup." in url:
        link_type = "MegaUp"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.megaup(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :</i></b>\n<code>{res}</code>\n\n"
            f"<b><u>NOTE : </u></b>\n<i>MegaUp has Cloudflare Protection Enabled.So Do not use this Link in Mirror Bots.Use it from your Device and downloading will start.</i>"
        )
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "sfile.mobi" in url:
        link_type = "Sfile.mobi"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.sfile(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif any(x in url for x in yandisk_list):
        link_type = "Yandex Disk"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.yandex_disk(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "osdn." in url:
        link_type = "OSDN"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.osdn(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "github.com" in url:
        link_type = "Github"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.github(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "mediafire." in url:
        link_type = "MediaFire"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.mediafire(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "zippyshare." in url:
        link_type = "ZippyShare"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.zippyshare(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "hxfile." in url:
        link_type = "HXFile"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.hxfile(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "files.im" in url:
        link_type = "FilesIm"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.filesIm(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "anonfiles." in url:
        link_type = "AnonFiles"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.anonfiles(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "letsupload." in url:
        link_type = "LetsUpload"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.letsupload(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "linkpoi." in url:
        link_type = "LinkPoi"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.linkpoi(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif any(x in url for x in fmed_list):
        link_type = "Fembed"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.fembed(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif any(x in url for x in sbembed_list):
        link_type = "SBEmbed"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.sbembed(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "mirrored." in url:
        link_type = "Mirrored"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.mirrored(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "uservideo." in url:
        link_type = "UserVideo"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.uservideo(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "antfiles." in url:
        link_type = "AntFiles"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.antfiles(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "streamtape." in url:
        link_type = "StreamTape"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.streamtape(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "sourceforge" in url:
        link_type = "SourceForge"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        if "master.dl.sourceforge.net" in url:
            res = await direct_link.sourceforge2(url)

            time_taken = get_readable_time(time() - start)
            LOGGER(__name__).info(f" Destination : {cmd} - {res}")
            b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
            await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
        else:
            res = await direct_link.sourceforge(url)

            time_taken = get_readable_time(time() - start)
            LOGGER(__name__).info(f" Destination : {cmd} - {res}")
            b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
            await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "androidatahost." in url:
        link_type = "AndroidataHost"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.androiddatahost(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "krakenfiles." in url:
        link_type = "KrakenFiles"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.krakenfiles(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "dropbox." in url:
        link_type = "DropBox"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.dropbox(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "pixeldrain." in url:
        link_type = "PixelDrain"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.pixeldrain(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif ("streamlare." or "sltube.") in url:
        link_type = "Streamlare"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.streamlare(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "pandafiles." in url:
        link_type = "PandaFiles"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.pandafile(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif is_fichier:
        link_type = "Fichier"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.fichier(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "upload.ee" in url:
        link_type = "UploadEE"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.uploadee(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "uptobox." in url:
        link_type = "Uptobox"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.uptobox(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "solidfiles." in url:
        link_type = "SolidFiles"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.solidfiles(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "hubcloud." in url:
        link_type = "HubCloud"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.hubcloud(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "mp4upload." in url:
        link_type = "MP4Upload"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.mp4upload(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "uploadbaz." in url:
        link_type = "UploadBaz"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.uploadbaz(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "uppit." in url:
        link_type = "Uppit"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.uppit(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "userscloud." in url:
        link_type = "UsersCloud"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.userscloud(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "bunkr.is" in url:
        link_type = "Bunkr.is"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.bunkr_cyber(url)
        res = await telegraph_paste(res)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Telegraph URL (containing Result) is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "cyberdrop." in url:
        link_type = "CyberDrop"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.bunkr_cyber(url)
        res = await telegraph_paste(res)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Telegraph URL (containing Result) is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "pixl.is" in url:
        link_type = "Pixl.is"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await direct_link.pixl(url)
        res = await telegraph_paste(res)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Telegraph URL (containing Result) is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "send.cm" in url:
        is_sendcm_folder = is_sendcm_folder_link(url)
        if is_sendcm_folder:
            link_type = "Sendcm Folder"
            LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
            a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
            await msg.edit(text=a)
            res = await direct_link.sendcm(url)
            res = await telegraph_paste(res)

            time_taken = get_readable_time(time() - start)
            LOGGER(__name__).info(f" Destination : {cmd} - {res}")
            b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Telegraph URL (containing Result) is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
            await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
        else:
            link_type = "Sendcm File"
            LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
            a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
            await msg.edit(text=a)
            res = await direct_link.sendcm(url)

            time_taken = get_readable_time(time() - start)
            LOGGER(__name__).info(f" Destination : {cmd} - {res}")
            b = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Your Direct-Download Link is :\n</i></b>{res}\n\n<i>Time Taken : {time_taken}</i>"
            await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif any(x in url for x in linkvertise_list):
        err3 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Short Link "
            f"Bypasser</b>\n\n<i>Use it with /bypass command followed by Link</i> "
        )
        await msg.edit(text=err3)
        return
    elif any(x in url for x in bypass_list):
        err4 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Short Link "
            f"Bypasser</b>\n\n<i>Use it with /bypass command followed by Link</i> "
        )
        await msg.edit(text=err4)
        return
    elif any(x in url for x in adfly_list):
        err5 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Short Link "
            f"Bypasser</b>\n\n<i>Use it with /bypass command followed by Link</i> "
        )
        await msg.edit(text=err5)
        return
    elif any(x in url for x in scrape_list):
        err6 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Site Scraper</b>\n\n<i>Use it "
            f"with /scrape command followed by Link</i> "
        )
        await msg.edit(text=err6)
        return
    else:
        await msg.delete()
        err7 = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b><i>Could not generate Direct Link for your URL</i></b>"
        await message.reply_text(text=err7, disable_web_page_preview=True, quote=True)
        return

    if (
        (DATABASE_URL and res) is not None
        and link_type not in DB_SAVE_PREVENTION
        and ("some error occurred" or "could not" or "error" or "not connect" or "not")
        not in str(res.lower())
    ):
        if not await DatabaseHelper().is_dblink_exist(url):
            await DatabaseHelper().add_new_dblink(url, res)
            LOGGER(__name__).info(f"Successfully Added - {url} - {res} to DB!")

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
