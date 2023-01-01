import datetime
import os

import aiofiles
from pyrogram import Client, enums, filters

from bot.config import *
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import ratelimit, user_commands
from bot.modules.pasting import katbin_paste

commands = ["paste", "p", f"paste@{BOT_USERNAME}", f"p@{BOT_USERNAME}"]
paste_usage = f"**Usage:** paste the text to katb.in website. Reply to a text file, text message or just type the text after commamd.\n\n**Example:** /paste type your text"


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
@ratelimit
async def paste(client, message):
    """
    Paste the text/document to KatBin
    """

    content = None
    replied_message = message.reply_to_message
    if len(message.command) > 1:
        content = message.text.split(None, 1)[1]
    elif replied_message:
        if replied_message.text:
            content = replied_message.text

        elif replied_message.document and any(
            format in replied_message.document.mime_type for format in ["text", "json"]
        ):
            await message.reply_to_message.download(
                os.path.join(os.getcwd(), "temp_file")
            )
            async with aiofiles.open("temp_file", "r+") as file:
                content = await file.read()
            os.remove("temp_file")
        else:
            return await message.reply_text(paste_usage, quote=True)

    elif len(message.command) < 2:
        return await message.reply_text(paste_usage, quote=True)

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

    paste_reply = await message.reply_text("Pasting...", quote=True)
    output = await katbin_paste(content)
    return await paste_reply.edit(f"{output}", disable_web_page_preview=True)
