from pyrogram import Client, filters
from pyrogram.types import Message

from bot.config import BOT_USERNAME, DATABASE_URL, prefixes
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import sudo_commands

cmds = ["db", f"db@{BOT_USERNAME}"]


@Client.on_message(filters.command(cmds, **prefixes))
@sudo_commands
async def all_users(_, message: Message):
    """
    Get information about Bot DataBase
    """
    if DATABASE_URL is not None:
        total_links = await DatabaseHelper().total_dblinks_count()
        total_users = await DatabaseHelper().total_users_count()
        if DatabaseHelper().check_db_connection() is not None:
            con_stats = True
        else:
            con_stats = False
        msg = f"<b>DataBase URL:</b> <code>{DATABASE_URL}</code>"
        msg += f"\n\n<b>Connection Status:</b> <code>{con_stats}</code>"
        msg += f"\n\n<b><i>No of Links Stored: </i></b>{total_links}"
        msg += f"\n\n<b><i>Total Bot Users: </i></b>{total_users}"
        await message.reply_text(text=msg, disable_web_page_preview=True, quote=True)
    else:
        err = "You have not provided a DB URL, so this function wont work!"
        await message.reply_text(text=err, disable_web_page_preview=True, quote=True)
