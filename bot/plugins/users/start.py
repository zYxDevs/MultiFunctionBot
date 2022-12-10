import datetime
import time

from pyrogram import Client, enums, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import BotStartTime
from bot.config import *
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import user_commands
from bot.helpers.functions import forcesub, get_readable_time
from bot.version import (
    __bot_version__,
    __gitrepo__,
    __license__,
    __pyro_layer__,
    __pyro_version__,
    __python_version__,
)

START_TEXT = """<b>Hey there!!</b>\n<b><i>I am the Multi Function Bot.</i></b>\n<i>Use buttons to navigate and know more about me :) \n\n**Bot is alive since {}.**</i>"""

COMMAND_TEXT = """**Here are the list of commands wich you can use in bot.\n**"""

ABOUT_TEXT = f"""• **Python Version** : {__python_version__}
• **Bot Version** : {__bot_version__}
• **Pyrogram Version** : {__pyro_version__}
• **Pyrogram Layer** : {__pyro_layer__}
• **License** : {__license__}

**Github Repo**: {__gitrepo__}"""

USER_TEXT = """🗒️ Documentation for commands available to user's

• /start: To Get this message

• /help: Alias command for start

• /ping: Ping the telegram api server.

• /image2pdf: Convert Image to PDF

• /rename: Rename a File in Telegram

• /tgupload: Upload a File to Telegram

• /takess: Take ScreenShot of a Webpage

• /wayback: Generate WayBack of a Webpage

• /bifm - Bypass Short Links using BIFM API

• /direct - Get Direct Link for various Supported URLs

• /bypass - Bypass Various Supported Shortened URLs

• /multi - Bypass Short Links using PyBypass Library

• /shorten - Get AdFree Shortened URLs of your Link

• /magnet - Extract Magnet from Torrent Websites

• /index - Extract Direct Links from Bhadoo Index Folder URLs

• /scrape - Extract Direct Links from Supported Sites

• /ytdl - (or /ytdlp) Extract DL Links using YT-DLP

• /gd - (or use /clone) Get GDrive Links for various Drive File Sharer
"""

SUDO_TEXT = """
🗒️ Documentation for Sudo Users commands.

• /db: Get information about Bot DataBase

• /speedtest: Check the internet speed of bot server

• /serverstats: Get the stats of server

• /stats: Alias command for serverstats

• /users: Get details about the Bot Users
"""

DEV_TEXT = """
🗒️ Documentation for Developers Commands.

• /addsudo - Add a user to the Bot sudo users list

• /removesudo - Remove a user to the Bot sudo users list

• /broadcast - Broadcast a message to all the Bot Users

• /update: To update the bot to latest commit from repository.

• /restart: Restart the bot.

• /log: To get the log file of bot.

• /ip: To get ip of the server where bot is running

• /shell: To run the terminal commands via bot.

• /exec: (or use /py) To run the python commands via bot
"""

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

prefixes = COMMAND_PREFIXES
commands = ["start", f"start@{BOT_USERNAME}", "help", f"help@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
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
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(START_BUTTON),
    )


@Client.on_callback_query()
async def botCallbacks(client, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    botuptime = get_readable_time(time.time() - BotStartTime)

    if CallbackQuery.data == "ABOUT_BUTTON":
        await CallbackQuery.edit_message_text(
            ABOUT_TEXT,
            reply_markup=InlineKeyboardMarkup(GOBACK_1_BUTTON),
            disable_web_page_preview=True,
        )

    elif CallbackQuery.data == "START_BUTTON":
        await CallbackQuery.edit_message_text(
            START_TEXT.format(botuptime), reply_markup=InlineKeyboardMarkup(START_BUTTON)
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
