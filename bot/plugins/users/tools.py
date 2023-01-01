import datetime
import glob
import os
import random
import urllib.request
from time import sleep

import img2pdf
import waybackpy
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from bot.config import *
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import ratelimit, user_commands
from bot.helpers.functions import forcesub

opener = urllib.request.build_opener()
opener.addheaders = [
    (
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    ),
    (
        "Accept",
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    ),
    ("Accept-Encoding", "gzip, deflate, br"),
    ("Accept-Language", "en-US,en;q=0.5"),
    ("Connection", "keep-alive"),
    ("Upgrade-Insecure-Requests", "1"),
]
urllib.request.install_opener(opener)


cmds = ["image2pdf", f"image2pdf@{BOT_USERNAME}"]
cmds2 = ["rename", f"rename@{BOT_USERNAME}"]
cmds3 = ["tgupload", f"tgupload@{BOT_USERNAME}"]
cmds4 = ["webss", f"webss@{BOT_USERNAME}"]
cmds5 = ["wayback", f"wayback@{BOT_USERNAME}"]


@Client.on_message(filters.command(cmds, **prefixes))
@user_commands
@ratelimit
async def image2pdf(client, message: Message):
    """
    Generate PDF of an Image
    """
    fsub = await forcesub(client, message)
    if not fsub:
        return
    msg = message.text.split(" ", 1)[1].rsplit(" ", 1)
    data = msg[1].replace("['", "").replace("']", "").replace(";", "").split("', '")
    name = msg[2]
    user_id = message.from_user.id
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
    os.mkdir(name)
    for _ in data:
        flnm = f"{name}/{data.index(_)}"
        urllib.request.urlretrieve(_, flnm + ".jpg")
    with open(f"{name}s.pdf", "wb") as f:
        f.write(img2pdf.convert(glob.glob(f"{name}/*.jpg")))
    await message.reply_document(f"{name}s.pdf")


@Client.on_message(filters.command(cmds2, **prefixes))
@user_commands
@ratelimit
async def rename(client, message: Message):
    """
    Rename a Telegram Media File
    """
    fsub = await forcesub(client, message)
    if not fsub:
        return
    if not message.reply_to_message:
        await message.reply("Please reply to a file/document")
    user_id = message.reply_to_message.id
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
    try:
        filename = message.text.replace(message.text.split(" ")[0], "")
    except Exception as e:
        await message.reply(f"{e}")
        return
    reply = message.reply_to_message
    if reply:
        x = await message.reply_text("Downloading.....")
        path = await reply.download(file_name=filename)
        await x.edit("Uploading.....")
        await message.reply_document(path)
        os.remove(path)


@Client.on_message(filters.command(cmds3, **prefixes))
@user_commands
@ratelimit
async def tgupload(client, message: Message):
    """
    Upload a URL to Telegram
    """
    fsub = await forcesub(client, message)
    if not fsub:
        return
    if message.reply_to_message:
        address = message.reply_to_message.text
    else:
        try:
            address = message.text.split()[1]
        except BaseException:
            await message.reply_text("Please Reply to a Url")
            return
    user_id = message.from_user.id
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
    x = await message.reply_text("Uploading to Telegram...")
    try:
        if address.startswith("http"):
            if address.endswith((".jpg", ".png", ".jpeg")):
                await message.reply_photo(address)
                await message.reply_document(address)
            elif address.endswith((".mp4", ".mkv", ".mov")):
                if len(str(message)) > 2:
                    await message.reply_document(address)
                else:
                    await message.reply_video(address)
            else:
                await message.reply_document(address)
        else:
            if True:
                await message.reply_document(address)
        await x.delete()
    except BaseException:
        await message.reply("No such File/Directory/Link")
        return


@Client.on_message(filters.command(cmds4, **prefixes))
@user_commands
@ratelimit
async def takess(client, message: Message):
    """
    Generate Screenshot of a Website
    """
    fsub = await forcesub(client, message)
    if not fsub:
        return
    try:
        if len(message.command) != 2:
            await message.reply_text("Give A Url To Fetch Screenshot.")
            return
        url = message.text.split(None, 1)[1]
        user_id = message.from_user.id
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
        m = await message.reply_text("**Taking Screenshot**")
        await m.edit("**Uploading**")
        try:
            await message.reply_photo(
                photo=f"https://webshot.amanoteam.com/print?q={url}", quote=False
            )
        except BaseException:
            return await m.edit("Sorry, Unable to Generate SS.")
        await m.delete()
    except Exception as e:
        await message.reply_text(f"Unknown Error Occurred!\nERROR: {e}")
        return


@Client.on_message(filters.command(cmds5, **prefixes))
@user_commands
@ratelimit
async def wayback(client, message: Message):
    """
    Generate WayBack of a Website
    """
    fsub = await forcesub(client, message)
    if not fsub:
        return
    try:
        if len(message.command) != 2:
            await message.reply_text("Give A Url To Get WayBack.")
            return
        url = message.text.split(None, 1)[1]
        user_id = message.from_user.id
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
        m = await message.reply_text("**Trying to get WayBack**")
        sleep(1)
        await m.edit("**Fetching**")
        user_agent = await getRandomUserAgent()
        try:
            wayback = waybackpy.Url(url, user_agent)
            archive = wayback.save()
            LOGGER(__name__).info("wayback success for: " + url)
            res = archive.archive_url
            reslt = f"<i>WayBack Generated,</i>\n<b>Check at</b> {res}"
            await m.edit(reslt)
        except Exception as r:
            err = f"WayBack Not Successful for : {url}, {str(r)}"
            LOGGER(__name__).error(err)
            await m.edit(err)
    except Exception as e:
        await m.delete()
        await message.reply_text(f"Unknown Error Occurred!\nERROR: {e}")
        return


async def getRandomUserAgent():
    agents = [
        "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.699.0 Safari/534.24",
        "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.220 Safari/535.1",
        "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1",
        "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (X11; CrOS i686 0.13.507) AppleWebKit/534.35 (KHTML, like Gecko) Chrome/13.0.763.0 Safari/534.35",
        "Mozilla/5.0 (X11; CrOS i686 0.13.587) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.14 Safari/535.1",
        "Mozilla/5.0 (X11; CrOS i686 1193.158.0) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7",
        "Mozilla/5.0 (X11; CrOS i686 12.0.742.91) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.93 Safari/534.30",
        "Mozilla/5.0 (X11; CrOS i686 12.433.109) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.93 Safari/534.30",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.34 Safari/534.24",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Ubuntu/10.04 Chromium/11.0.696.0 Chrome/11.0.696.0 Safari/534.24",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Ubuntu/10.10 Chromium/12.0.703.0 Chrome/12.0.703.0 Safari/534.24",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21",
        "Opera/9.80 (Windows NT 5.1; U; sk) Presto/2.5.22 Version/10.50",
        "Opera/9.80 (Windows NT 5.1; U; zh-sg) Presto/2.9.181 Version/12.00",
        "Opera/9.80 (Windows NT 5.1; U; zh-tw) Presto/2.8.131 Version/11.10",
        "Opera/9.80 (Windows NT 5.1; U;) Presto/2.7.62 Version/11.01",
        "Opera/9.80 (Windows NT 5.2; U; en) Presto/2.6.30 Version/10.63",
        "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51",
        "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.6.30 Version/10.61",
        "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.7.62 Version/11.01",
        "Opera/9.80 (X11; Linux x86_64; U; pl) Presto/2.7.62 Version/11.00",
        "Opera/9.80 (X11; Linux x86_64; U; Ubuntu/10.10 (maverick); pl) Presto/2.7.62 Version/11.01",
        "Opera/9.80 (X11; U; Linux i686; en-US; rv:1.9.2.3) Presto/2.2.15 Version/10.10",
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.117 Mobile Safari/537.36",
    ]
    return agents[random.randint(0, len(agents) - 1)]
