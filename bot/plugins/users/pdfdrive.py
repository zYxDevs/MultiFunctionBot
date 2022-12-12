import datetime
import os

import requests
from pyrogram import Client, enums, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaDocument,
    InputMediaPhoto,
)

from bot.config import BOT_USERNAME, DATABASE_URL, LOG_CHANNEL, prefixes
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import user_commands
from bot.helpers.functions import forcesub
from bot.logging import LOGGER
from bot.modules import pdfdrivefetch

data = []


class save:
    msgid: str
    books: list


def storedata(msgid, books):
    new = save()
    new.msgid = msgid
    new.books = books
    data.append(new)


def getdata(msgid):
    for ele in data:
        if ele.msgid == msgid:
            return ele.books
    return 0


commands = ["pdfdrive", f"pdfdrive@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
async def pdfdrive(client, message):
    global search
    fsub = await forcesub(client, message)
    if not fsub:
        return

    reply_to = message.reply_to_message

    if len(message.command) > 1:
        search = message.text.split(None, 1)[1]
    elif reply_to is not None:
        search = reply_to.text
    elif len(message.command) < 2 or reply_to is None:
        err = "<b><i>Please send a query or reply to an query to proceed!</i></b>"
        await message.reply_text(text=err, disable_web_page_preview=True, quote=True)
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

    books = pdfdrivefetch.getpage(search)
    msg = message.send_photo(
        message.chat.id,
        books[0].link,
        f"**{books[0].title}**\n\n__Year: {books[0].year}\nSize: {books[0].size}\nPages: {books[0].pages}\nDownloads: {books[0].downloads}__",
        reply_to_message_id=message.id,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="⬅️", callback_data="-1"),
                    InlineKeyboardButton(text="✅", callback_data="D0"),
                    InlineKeyboardButton(text="➡️", callback_data="+1"),
                ]
            ]
        ),
    )
    storedata(msg.id, books)


@Client.on_callback_query()
async def pdfdrive_callback(message, client):
    books = getdata(client.message.id)
    if books == 0:
        wrongimage = "https://graph.org/file/fddb76c4e758df3dfad37.png"
        client.edit_message_media(
            message.chat.id,
            message.id,
            InputMediaPhoto(wrongimage, "__Out of Date, Search Again__"),
        )
        return

    if client.data[0] == "D":
        choose = int(client.data.replace("D", ""))
        client.edit_message_text(message.chat.id, message.id, "__Downloading__")
        durl = pdfdrivefetch.getdownlink(books[choose])
        res = requests.get(durl)
        with open(f"{books[choose].title}.pdf", "wb") as file:
            file.write(res.content)
        res = requests.get(books[choose].coverlink)
        with open(f"{books[choose].title}.jpg", "wb") as file:
            file.write(res.content)
        client.edit_message_text(message.chat.id, message.id, "__Uploading__")
        client.edit_message_media(
            message.chat.id,
            message.id,
            InputMediaDocument(
                f"{books[choose].title}.pdf",
                thumb=f"{books[choose].title}.jpg",
                caption=f"**{books[choose].title}**",
            ),
        )
        os.remove(f"{books[choose].title}.pdf")
        os.remove(f"{books[choose].title}.jpg")
        return

    choose = int(client.data)
    client.edit_message_media(
        message.chat.id,
        message.id,
        InputMediaPhoto(
            books[choose].link,
            f"**{books[choose].title}**\n\n__Year: {books[choose].year}\nSize: {books[choose].size}\nPages: {books[choose].pages}\nDownloads: {books[choose].downloads}__",
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="⬅️", callback_data=str(choose - 1)),
                    InlineKeyboardButton(text="✅", callback_data=f"D{choose}"),
                    InlineKeyboardButton(text="➡️", callback_data=str(choose + 1)),
                ]
            ]
        ),
    )
