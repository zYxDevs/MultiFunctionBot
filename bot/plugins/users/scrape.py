import datetime
import time
from re import search

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from bot.config import BOT_USERNAME, DATABASE_URL, LOG_CHANNEL, prefixes
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import ratelimit, user_commands
from bot.helpers.functions import forcesub, get_readable_time
from bot.modules.gdrive_direct import pahe
from bot.modules.lists import *
from bot.modules.regex import *
from bot.modules.scraper import *

commands = ["scrape", f"scrape@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
@ratelimit
async def scrape(client, message: Message):
    """
    Extract Download/GDrive/Shortened Links from Supported Sites
    """
    global time_taken, des_url
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

    start = time.time()
    msg_text = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Processing your URL.....</b>"
    msg = await message.reply_text(
        text=msg_text, disable_web_page_preview=True, quote=True
    )
    LOGGER(__name__).info(f" Received : {cmd} - {url}")
    time.sleep(1)
    supp_index = is_bhadoo_index(url)
    if supp_index:
        link_type = "Bhadoo Index"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        res = await index_scrap(url)
        des_url = await telegraph_paste(res)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "animeremux." in url:
        link_type = "AnimeRemux"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await animeremux_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif ("atishmkv." or "atish.mkv") in url:
        link_type = "AtishMKV"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await atishmkv_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "benzmovies." in url:
        link_type = "BenzMovies"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await benzmovies_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "cinevez." in url:
        link_type = "Cinevez"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await cinevez_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "cinevood." in url:
        link_type = "Cinevood"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await cinevood_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "filecrypt." in url:
        link_type = "FileCrypt"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await filecrypt_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif ("htpmovies." and "/exit.php?url=") in url:
        link_type = "HTPMovies DL"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await htpmovies(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "igg-games." in url:
        link_type = "IGG Games"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await igggames_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "moviesboss." in url:
        link_type = "MoviesBoss"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await moviesboss_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "moviesdrama." in url:
        link_type = "MoviesDrama"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await moviesdrama_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "olamovies." in url:
        link_type = "OlaMovies"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await olamovies_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "psa." in url:
        abc = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>PSA</i>"
        await msg.edit(text=abc)
        """ des_url = await psa_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {des_url}")
        xyz = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>" """
        xyz = "<b>PSA Scraper has been patched for now!</b>"
        await message.reply_text(text=xyz, disable_web_page_preview=True, quote=True)
    elif "taemovies." in url:
        link_type = "TaeMovies"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await taemovies_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "tamiltvtoons." in url:
        link_type = "TamilTVToons"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await tamiltvtoons_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "teleguflix." in url:
        link_type = "TeleguFlix"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await teleguflix_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "toonworld4all." in url:
        link_type = "ToonWorld4All"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await toonworld4all_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "sharespark." in url:
        link_type = "Sharerspark"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await sharespark_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif ("privatemoviez." and "/secret?data=") in url:
        link_type = "PrivateMoviez DL"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await privatemoviez(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "moviesmod." in url:
        link_type = "MoviesMod"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await moviesmod_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "skymovieshd." in url:
        link_type = "SkyMoviesHD"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await skymovieshd_scrap(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
        await message.reply_text(text=b, disable_web_page_preview=True, quote=True)
    elif "pahe." in url:
        link_type = "Pahe"
        a = f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>Bot has received the following link</b> :\n<code>{url}</code>\n\n<b>Link Type</b> : <i>{link_type}</i>"
        await msg.edit(text=a)
        des_url = await pahe(url)
        time_taken = get_readable_time(time.time() - start)
        LOGGER(__name__).info(f" Destination : {cmd} - {link_type} - {des_url}")
        b = f"<b>Telegraph URL(with Result):\n</b> {des_url}\n\n<i>Time Taken : {time_taken}</i>"
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
    elif any(x in url for x in linkvertise_list):
        err7 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Short Link "
            f"Bypasser</b>\n\n<i>Use it with /bypass command followed by Link</i> "
        )
        await msg.edit(text=err7)
        return
    elif any(x in url for x in bypass_list):
        err8 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Short Link "
            f"Bypasser</b>\n\n<i>Use it with /bypass command followed by Link</i> "
        )
        await msg.edit(text=err8)
        return
    elif any(x in url for x in adfly_list):
        err9 = (
            f"<b>Dear</b> {uname} (ID: {uid}),\n\n<b>This Link is Supported by the Short Link "
            f"Bypasser</b>\n\n<i>Use it with /bypass command followed by Link</i> "
        )
        await msg.edit(text=err9)
        return
    else:
        await msg.delete()
        xyz = "This Command does not support this Link!"
        await message.reply_text(text=xyz, disable_web_page_preview=True, quote=True)
        return

    try:
        logmsg = f"<b><i>User:</i></b> {user_}\n<b><i>User ID:</i></b><code>{user_id}</code>\n<i>User URL:</i> {url}\n<i>Command:</i> {cmd}\n<i>Destination URL:</i> {des_url}\n\n<b><i>Time Taken:</i></b> {time_taken} "
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=logmsg,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception as err:
        LOGGER(__name__).error(f"BOT Log Channel Error: {err}")
