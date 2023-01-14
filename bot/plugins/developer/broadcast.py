import asyncio

from pyrogram import Client, filters

from bot.config import BOT_USERNAME, prefixes
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import dev_commands
from bot.logging import LOGGER

Broadcast_IDs = {}

commands = ["broadcast", f"broadcast@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@dev_commands
async def broadcast(c, m):
    """
    Broadcast the message via bot to bot users
    """

    if not (broadcast_msg := m.reply_to_m):
        broadcast_usage = f"Reply with command /broadcast to the message you want to broadcast.\n\n/broadcast loud - To Enable Notificatons"
        return await m.reply_text(broadcast_usage, quote=True)

    proses_msg = await m.reply_text(
        "**Broadcasting started. Please wait for few minutes for it to get completed.**",
        quote=True,
    )

    disable_notification = True
    commands = m.command

    if len(commands) > 3:
        return await proses_msg.edit("Invalid Command")

    for command in m.command:
        if command.lower() == "loud":
            disable_notification = False

    total_list = await DatabaseHelper().get_all_users()

    failed = 0
    success = 0

    for __id in total_list:
        try:
            await broadcast_msg.copy(
                __id, broadcast_msg.caption, disable_notification=disable_notification
            )
            success += 1
            await asyncio.sleep(0.3)
        except Exception as error:
            LOGGER(__name__).error(str(error))
            failed += 1

    return await proses_msg.edit(
        f"**The message has been successfully broadcasted.**\n\nTotal success = {success}\nTotal Failure = {failed}"
    )
