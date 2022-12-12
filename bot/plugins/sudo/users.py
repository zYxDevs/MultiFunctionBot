from pyrogram import Client, filters
from pyrogram.types import Message

from bot.config import BOT_USERNAME, DATABASE_URL, OWNER_ID, SUDO_USERS, prefixes
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import sudo_commands

cmds = ["users", f"users@{BOT_USERNAME}"]


@Client.on_message(filters.command(cmds, **prefixes))
@sudo_commands
async def all_users(_, message: Message):
    """
    Get the bot owner and sudo users list
    """
    usera = "\n".join(f"<code>{user}</code>" for user in OWNER_ID)
    msg = f"<b><u>Owner IDs:</u></b>\n{usera}"
    msg += "\n"
    userb = "\n".join(f"<code>{user}</code>" for user in SUDO_USERS)
    msg += f"<b><u>Sudo Users:</u></b>\n{userb}"
    if DATABASE_URL is not None:
        total_users = await DatabaseHelper().total_users_count()
        msg += f"\n<b><i>Total Bot Users: </i></b>{total_users}"
    await message.reply_text(text=msg, disable_web_page_preview=True, quote=True)
