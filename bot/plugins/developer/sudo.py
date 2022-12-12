from pyrogram import Client, filters
from pyrogram.types import Message

from bot.config import BOT_USERNAME, DATABASE_URL, SUDO_USERS, prefixes
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import dev_commands
from bot.logging import LOGGER

cmds_addsudo = ["addsudo", f"addsudo@{BOT_USERNAME}"]
cmds_rmsudo = ["removesudo", f"removesudo@{BOT_USERNAME}"]


@Client.on_message(filters.command(cmds_addsudo, **prefixes))
@dev_commands
async def sudo_user(_, message: Message):
    """
    Add a user to the Bot sudo users list
    """
    msg_arg = message.text.replace("  ", " ")
    msg_args = msg_arg.split(" ", maxsplit=1)
    user_id = ""
    reply_to = message.reply_to_message
    if len(msg_args) == 2:
        user_id = int(msg_args[1])
    elif reply_to:
        user_id = reply_to.from_user.id
    if user_id:
        if user_id in SUDO_USERS:
            msg = f"<b><i>Already in Sudo Users List!</i></b>"
        elif DATABASE_URL is not None:
            msg = await DatabaseHelper().auth_user(user_id)
            SUDO_USERS.add(user_id)
        else:
            SUDO_USERS.add(user_id)
            LOGGER(__name__).info(f"Added {user_id} to Sudo Users List!")
            msg = f"<b><i>Successfully added {user_id} to Sudo Users List!</i></b>"
    else:
        msg = "<b>Only a User ID can be added to Sudo List!</b>"
    await message.reply_text(text=msg, disable_web_page_preview=True, quote=True)


@Client.on_message(filters.command(cmds_rmsudo, **prefixes))
@dev_commands
async def rmsudo_user(_, message: Message):
    """
    Remove a user to the Bot sudo users list
    """
    msg_arg = message.text.replace("  ", " ")
    msg_args = msg_arg.split(" ", maxsplit=1)
    user_id = ""
    reply_to = message.reply_to_message
    if len(msg_args) == 2:
        user_id = int(msg_args[1])
    elif reply_to:
        user_id = reply_to.from_user.id
    if user_id:
        if user_id in SUDO_USERS:
            if DATABASE_URL is not None:
                msg = await DatabaseHelper().unauth_user(user_id)
            else:
                LOGGER(__name__).info(f"Removed {user_id} from Sudo Users List!")
                msg = f"<b><i>Successfully removed {user_id} from Sudo Users List!</i></b>"
            SUDO_USERS.remove(user_id)
        else:
            msg = "<b><i>User does not exist in Sudo Users List!</i></b>"
    else:
        msg = "<b>Only a User ID can be removed to Sudo List!</b>"
    await message.reply_text(text=msg, disable_web_page_preview=True, quote=True)
