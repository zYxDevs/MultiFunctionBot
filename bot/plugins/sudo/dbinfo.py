from pyrogram import Client, filters
from pyrogram.types import Message

from bot.config import BOT_USERNAME, COMMAND_PREFIXES, DATABASE_URL
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import dev_commands, sudo_commands

prefixes = COMMAND_PREFIXES
cmds = ["db", f"db@{BOT_USERNAME}"]


@Client.on_message(filters.command(cmds, **prefixes))
@dev_commands
@sudo_commands
async def all_users(_, message: Message):
    """
    Get total no of links stored in DB
    """
    if DATABASE_URL is not None:
        total_links = await DatabaseHelper().total_dblinks_count()
        msg = f"\n<b><i>No of Links Stored: </i></b>{total_links}"
        await message.reply_text(text=msg, disable_web_page_preview=True, quote=True)
    else:
        err = "You have not provided a DB URL, so this function wont work!"
        await message.reply_text(text=err, disable_web_page_preview=True, quote=True)
