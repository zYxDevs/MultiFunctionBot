import shutil
import time

import psutil
from pyrogram import Client, filters
from pyrogram.types import Message

from bot import BotStartTime
from bot.config import *
from bot.helpers.decorators import sudo_commands
from bot.helpers.functions import (
    get_readable_file_size,
    get_readable_size,
    get_readable_time,
)

commands = [
    "stats",
    f"stats@{BOT_USERNAME}",
    "serverstats",
    f"serverstats@{BOT_USERNAME}",
]


@Client.on_message(filters.command(commands, **prefixes))
@sudo_commands
async def update(client, message: Message):
    currentTime = get_readable_time(time.time() - BotStartTime)
    total, used, free = shutil.disk_usage(".")
    total = get_readable_size(total)
    used = get_readable_size(used)
    free = get_readable_size(free)

    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)

    pcores = psutil.cpu_count(logical=False)
    tcores = psutil.cpu_count(logical=True)

    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent

    await message.reply_text(
        f"**≧◉◡◉≦ Bot is Up and Running successfully.**\n\n×⌚ <b>Bot Uptime:</b> `{currentTime}`\n×🗄️ <b>Total Disk Space:</b> `{total}`\n×🗃️ <b>Used:</b> `{used}({disk_usage}%)`\n×🗃️ <b>Free:</b> `{free}`\n\n×🖥️ <b>CPU Usage:</b> `{cpu_usage}%`\n×⛏️ <b>RAM Usage:</b> `{ram_usage}%`\n\n×💻 <b>Physical Cores:</b> {pcores}\n×💻 <b>Total Cores:</b> {tcores}\n\n× 🔻 <b>DL:</b> `{recv}` | 🔺 <b>UL:</b> `{sent}`",
        quote=True,
    )
