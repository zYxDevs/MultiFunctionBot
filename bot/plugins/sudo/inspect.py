from pyrogram import Client, filters
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from bot.config import *
from bot.helpers.decorators import sudo_commands
from bot.modules.pasting import katbin_paste

commands = ["inspect", f"inspect@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@sudo_commands
async def inspect(_, message: Message):
    """
    Inspect the message and give reply in json format
    """

    try:
        await message.reply_text(message, quote=True)
    except MessageTooLong:
        output = await katbin_paste(message)
        await message.reply_text(output, quote=True)
