import os
import platform
import subprocess
import sys
import time
from asyncio import get_event_loop, new_event_loop, set_event_loop

import uvloop
from pyrogram import Client, __version__
from pyrogram.raw.all import layer

from bot.config import API_HASH, API_ID, BOT_TOKEN, BOT_USERNAME
from bot.logging import LOGGER

system = platform.system()
BotStartTime = time.time()
plugins = dict(root="bot/plugins")

if os.path.exists("logs.txt"):
    with open("logs.txt", "r+") as f:
        f.truncate(0)

if not os.path.exists("Downloads"):
    os.makedirs("Downloads")

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

uvloop.install()

LOGGER(__name__).info("Installing Bot Requirements...")
subprocess.run(
    ["pip3", "install", "--no-cache-dir", "-r", "requirements.txt", "--upgrade"]
)

LOGGER(__name__).info("Setting Upload Module Permissions...")
if system == "Windows":
    subprocess.run(["icacls", "upload_module_x64", "/grant", "*:F"])
elif system in ["Linux", "Darwin"]:
    subprocess.run(["chmod", "777", "./upload_module_x64"])
LOGGER(__name__).info("Initiating the Client!")
LOGGER(__name__).info(BANNER)
LOGGER(__name__).info(
    f"Pyrogram v{__version__} (Layer {layer}) started on @{BOT_USERNAME}."
)
LOGGER(__name__).info("Telegram Bot Started.")

bot = Client(
    "MultiFunctionBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=plugins,
)  # https://docs.pyrogram.org/topics/smart-plugins
