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
from bot.modules import bypasser
from bot.modules.lists import *
from bot.modules.regex import *

commands = ["bypass", f"bypass@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
@ratelimit
async def bypass(client, message: Message):
    """
    Bypass Various Supported Shortened URLs
    """
    global link_type, res
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
            LOGGER(__name__).info(f"Successfully Bypassed - DB:True - {result}")
            b = f"<b>Bypassed Result :\n</b>{result}\n\n<i>Time Taken : {time_taken}</i>\n<i>Result Added on:</i>{add_date}"
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

    if "adrinolinks." in url:
        link_type = "AdrinoLinks"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.adrinolinks(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "droplink." in url or "droplinks." in url:
        link_type = "DropLinks"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.droplink(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "dulink." in url:
        link_type = "Dulink"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.dulink(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "ez4short." in url:
        link_type = "Ez4Short"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.ez4short(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "gplink." in url or "gplinks." in url:
        link_type = "GPLinks"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.gplinks(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "krownlinks." in url:
        link_type = "KrownLinks"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.krownlinks(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "linkbnao." in url:
        link_type = "LinkBnao"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.linkbnao(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif any(x in url for x in linkvertise_list):
        link_type = "Linkvertise"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.linkvertise(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif any(x in url for x in adfly_list):
        link_type = "AdFly"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.adfly(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "gyanilinks." in url or "gyanilink" in url:
        link_type = "GyaniLinks"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.gyanilinks(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "htpmovies." in url and "/exit.php?url" in url:
        link_type = "HTPMovies DL"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.htpmovies(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "privatemoviez." in url and "/secret?data=" in url:
        link_type = "PrivateMoviez DL"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.privatemoviez(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "hypershort." in url:
        link_type = "HyperShort"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.hypershort(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "sirigan.my.id" in url:
        link_type = "Sirigan.my.id"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.sirigan(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif ("ouo.io" or "ouo.press") in url:
        link_type = "Ouo"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.ouo(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif any(x in url for x in shst_list):
        link_type = "Shorte.st"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.shorte(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "rocklinks." in url:
        link_type = "RockLinks"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.rocklinks(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "mdisk.pro" in url:
        link_type = "MDiskPro"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.mdiskpro(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif ("gtlinks." or "loan.kinemaster./?token=" or "theforyou.in/?token=") in url:
        url = url.replace("&m=1", "")
        link_type = "GTLinks"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.gtlinks(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "gyanilinks." in url:
        link_type = "GyaniLinks"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.gyanilinks(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "shareus." in url:
        link_type = "Shareus"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.shareus(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "short2url." in url:
        link_type = "Short2url"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.short2url(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "shortingly." in url:
        link_type = "Shortingly"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.shortingly(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "tnlink." in url:
        link_type = "TnLink"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.tnlink(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "xpshort." in url:
        link_type = "XpShort"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.xpshort(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "pkin." in url:
        link_type = "Pkin"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.pkin(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "rewayatcafe." in url:
        link_type = "RewayatCafe"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.rewayatcafe(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "shortly." in url:
        link_type = "Shortly"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.shortly(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "try2link." in url:
        link_type = "Try2Link"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.try2link(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "thinfi." in url:
        link_type = "ThinFi"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.thinfi(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "urlsopen." in url:
        link_type = "UrlsOpen"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.urlsopen(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif ("vearnl." or "urlearn." or "earnl.") in url:
        link_type = "Vearnl"
        LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await bypasser.vearnl(url)

        time_taken = get_readable_time(time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {res}")
        b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif any(x in url for x in yandisk_list):
        err3 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Direct Link "
            f"Generator</b>\n\n<i>Use it with /direct command followed by Link</i> "
        )
        await msg.edit(text=err3)
        return
    elif any(x in url for x in fmed_list):
        err4 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Direct Link "
            f"Generator</b>\n\n<i>Use it with /direct command followed by Link</i> "
        )
        await msg.edit(text=err4)
        return
    elif any(x in url for x in sbembed_list):
        err5 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Direct Link "
            f"Generator</b>\n\n<i>Use it with /direct command followed by Link</i> "
        )
        await msg.edit(text=err5)
        return
    elif any(x in url for x in directdl_list):
        err6 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Direct Link "
            f"Generator</b>\n\n<i>Use it with /direct command followed by Link</i> "
        )
        await msg.edit(text=err6)
        return
    elif any(x in url for x in scrape_list):
        err7 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Site Scraper</b>\n\n<i>Use it "
            f"with /scrape command followed by Link</i> "
        )
        await msg.edit(text=err7)
        return
    else:
        try:
            link_type = "Script Generic"
            LOGGER(__name__).info(f" Received : {cmd} - {link_type} - {url}")
            a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n<b>Link Type</b> : <i>{link_type}</i>"
            await msg.edit(text=a)
            res = await bypasser.script(url)

            time_taken = get_readable_time(time() - start)
            LOGGER(__name__).info(f" Destination : {cmd} - {res}")
            b = f"<b>Bypassed Result :\n</b>{res}\n\n<i>Time Taken : {time_taken}</i>"
            await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
        except BaseException:
            err = "<b><i>Could not find Bypass for your URL!</i></b>"
            await msg.edit(text=err)
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
        logmsg = f"<b><i>User:</i></b> {user_}\n<b><i>User ID:</i></b><code>{user_id}</code>\n<i>User URL:</i> {url}\n<i>Command:</i> {cmd}\n<i>Destination URL:</i> {res}\n\n<b><i>Time Taken:</i></b> {time_taken} "
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=logmsg,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception as err:
        LOGGER(__name__).error(f"BOT Log Channel Error: {err}")
