import datetime
import time

from pyrogram import Client, enums, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import BotStartTime
from bot.config import *
from bot.helpers.constants import (
    ABOUT_TEXT,
    COMMAND_TEXT,
    DEV_TEXT,
    START_TEXT,
    SUDO_TEXT,
    USER_TEXT,
)
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import ratelimit, user_commands
from bot.helpers.functions import forcesub, get_readable_time
from bot.version import __gitrepo__

START_BUTTON = [
    [
        InlineKeyboardButton("📖 Commands", callback_data="COMMAND_BUTTON"),
        InlineKeyboardButton("👨‍💻 About me", callback_data="ABOUT_BUTTON"),
    ],
    [
        InlineKeyboardButton(
            "🔭 Original Repo",
            url=f"{__gitrepo__}",
        )
    ],
]

COMMAND_BUTTON = [
    [
        InlineKeyboardButton("Users", callback_data="USER_BUTTON"),
        InlineKeyboardButton("Sudo", callback_data="SUDO_BUTTON"),
    ],
    [InlineKeyboardButton("Developer", callback_data="DEV_BUTTON")],
    [InlineKeyboardButton("🔙 Go Back", callback_data="START_BUTTON")],
]

GOBACK_1_BUTTON = [[InlineKeyboardButton("🔙 Go Back", callback_data="START_BUTTON")]]

GOBACK_2_BUTTON = [[InlineKeyboardButton("🔙 Go Back", callback_data="COMMAND_BUTTON")]]


commands = ["start", f"start@{BOT_USERNAME}", "help", f"help@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
@ratelimit
async def start(client, message):
    fsub = await forcesub(client, message)
    if not fsub:
        return
    botuptime = get_readable_time(time.time() - BotStartTime)
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
    await message.reply_text(
        text=START_TEXT.format(botuptime),
        quote=True,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(START_BUTTON),
    )


@Client.on_callback_query(filters.regex("_BUTTON"))
@ratelimit
async def botCallbacks(client, CallbackQuery):
    clicker_user_id = CallbackQuery.from_user.id
    user_id = CallbackQuery.message.reply_to_message.from_user.id
    if clicker_user_id != user_id:
        return await CallbackQuery.answer("This command is not initiated by you.")

    botuptime = get_readable_time(time.time() - BotStartTime)

    if CallbackQuery.data == "ABOUT_BUTTON":
        await CallbackQuery.edit_message_text(
            ABOUT_TEXT,
            reply_markup=InlineKeyboardMarkup(GOBACK_1_BUTTON),
            disable_web_page_preview=True,
        )

    elif CallbackQuery.data == "START_BUTTON":
        await CallbackQuery.edit_message_text(
            START_TEXT.format(botuptime),
            reply_markup=InlineKeyboardMarkup(START_BUTTON),
        )

    elif CallbackQuery.data == "COMMAND_BUTTON":
        await CallbackQuery.edit_message_text(
            COMMAND_TEXT, reply_markup=InlineKeyboardMarkup(COMMAND_BUTTON)
        )

    elif CallbackQuery.data == "USER_BUTTON":
        await CallbackQuery.edit_message_text(
            USER_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
        )

    elif CallbackQuery.data == "SUDO_BUTTON":
        if user_id not in SUDO_USERS:
            return await CallbackQuery.answer(
                "You are not in the Bot sudo user list.", show_alert=True
            )
        else:
            await CallbackQuery.edit_message_text(
                SUDO_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
            )

    elif CallbackQuery.data == "DEV_BUTTON":
        if user_id not in OWNER_ID:
            return await CallbackQuery.answer(
                "This is A developer restricted command.", show_alert=True
            )
        else:
            await CallbackQuery.edit_message_text(
                DEV_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
            )
