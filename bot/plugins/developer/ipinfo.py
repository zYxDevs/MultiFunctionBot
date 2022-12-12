import httpx
from pyrogram import Client, filters
from pyrogram.types import Message

from bot.config import *
from bot.helpers.decorators import dev_commands

commands = ["ip", f"ip@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@dev_commands
async def ipinfo(client, message: Message):
    """
    Give ip of the server where bot is running.
    """

    async with httpx.AsyncClient() as client:
        response = await client.get("http://ipinfo.io/ip")

    await message.reply_text(
        f"IP Adress of the server bot server is: `{response.text}`", quote=True
    )
