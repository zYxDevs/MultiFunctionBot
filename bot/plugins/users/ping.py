import time
from datetime import datetime

import httpx
from pyrogram import Client, filters
from pyrogram.types import Message

from bot import BotStartTime
from bot.config import *
from bot.helpers.decorators import ratelimit, user_commands
from bot.helpers.functions import get_readable_time

commands = ["ping", f"ping@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
@ratelimit
async def ping(_, message: Message):
    """
    Checks ping speed to bot API
    """

    pong_reply = await message.reply_text("pong!", quote=True)

    start = datetime.now()
    async with httpx.AsyncClient() as client:
        await client.get("http://api.telegram.org")
    end = datetime.now()

    botuptime = get_readable_time(time.time() - BotStartTime)
    pong = (end - start).microseconds / 1000

    return await pong_reply.edit(
        f"**Ping Time:** `{pong}`ms | **Bot is alive since:** `{botuptime}`"
    )
