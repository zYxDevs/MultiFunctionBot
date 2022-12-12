import os
import sys
import time
from asyncio import get_event_loop, new_event_loop, set_event_loop

import nest_asyncio
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from pyrogram import Client, __version__
from pyrogram.raw.all import layer

from bot.config import API_HASH, API_ID, BOT_TOKEN, BOT_USERNAME
from bot.logging import LOGGER

nest_asyncio.apply()

BotStartTime = time.time()
plugins = dict(root="bot/plugins")

if os.path.exists("logs.txt"):
    with open("logs.txt", "r+") as f:
        f.truncate(0)

try:
    loop = get_event_loop()
except RuntimeError:
    set_event_loop(new_event_loop())
    loop = get_event_loop()


if sys.version_info[0] < 3 or sys.version_info[1] < 7:
    VERSION_ASCII = """
  =============================================================
  "You MUST need to be on python 3.7 or above, shutting down the bot...
  =============================================================
  """
    LOGGER(__name__).critical(VERSION_ASCII)
    sys.exit(1)


BANNER = """
________________________________________________________________________________________________________________
|   _____        .__   __  .__  ___________                   __  .__                __________        __      |
|   /     \  __ __|  |_/  |_|__| \_   _____/_ __  ____   _____/  |_|__| ____   ____   \______   \ _____/  |_   |
|  /  \ /  \|  |  \  |\   __\  |  |    __)|  |  \/    \_/ ___\   __\  |/  _ \ /    \   |    |  _//  _ \   __\  |
| /    Y    \  |  /  |_|  | |  |  |     \ |  |  /   |  \  \___|  | |  (  <_> )   |  \  |    |   (  <_> )  |    |
| \____|__  /____/|____/__| |__|  \___  / |____/|___|  /\___  >__| |__|\____/|___|  /  |______  /\____/|__|    |
|         \/                          \/             \/     \/                    \/          \/               |
|______________________________________________________________________________________________________________|
"""
# https://patorjk.com/software/taag/#p=display&f=Graffiti&t=Multi%20Function%20Bot


PLAY = sync_playwright().start()
BROWSER = PLAY.chromium.launch_persistent_context(
    user_data_dir="/tmp/playwright", headless=False
)
PAGE = BROWSER.new_page()
stealth_sync(PAGE)


def get_input_box():
    """Get the child textarea of `PromptTextarea__TextareaWrapper`"""
    return PAGE.query_selector("textarea")


def is_logged_in():
    # See if we have a textarea with data-id="root"
    return get_input_box() is not None


def send_message_to_browser(message):
    # Send the message
    box = get_input_box()
    box.click()
    box.fill(message)
    box.press("Enter")


LOGGER(__name__).info("Installing Bot Requirements...")
os.system("pip3 install --no-cache-dir -r requirements.txt --upgrade")
LOGGER(__name__).info("Initiating the Client!")
LOGGER(__name__).info(BANNER)
LOGGER(__name__).info(
    f"Pyrogram v{__version__} (Layer {layer}) started on {f'@{BOT_USERNAME}'}."
)
LOGGER(__name__).info("Telegram Bot Started.")

bot = Client(
    "MultiFunctionBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=plugins,
)  # https://docs.pyrogram.org/topics/smart-plugins
