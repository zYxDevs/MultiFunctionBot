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

• /start - To Get this message

• /help - Alias command for start

• /dalle - Generate images from a text prompt using DALLE-Mini

• /upload - Upload a Telegram File to various Free File Hosting Servers

• /bifm - Bypass Short Links using BIFM API

• /direct - Get Direct Link for various Supported URLs

• /bvip - Bypass Short Links using Bypass.vip API

• /bypass - Bypass Various Supported Shortened URLs

• /multi - Bypass Short Links using PyBypass Library

• /shorten - Get AdFree Shortened URLs of your Link

• /magnet - Extract Magnet from Torrent Websites

• /index - Extract Direct Links from Bhadoo Index Folder URLs

• /scrape - Extract Direct Links from Supported Sites

• /ytdl - (or /ytdlp) Extract DL Links using YT-DLP

• /gd - (or use /clone) Get GDrive Links for various Drive File Sharer

• /headfone - Scrape Headfone.co.in to get Direct Links of an Album

• /hungama - Get Download link and Metadata of a Hungama Link

• /ping - Ping the telegram api server.

• /image2pdf - Convert Image to PDF

• /rename - Rename a File in Telegram

• /tgupload - Upload a File to Telegram

• /takess - Take ScreenShot of a Webpage

• /wayback - Generate WayBack of a Webpage

• /paste: Paste the text/document to KatBin
"""

SUDO_TEXT = """
🗒️ Documentation for Sudo Users commands.

• /db: Get information about Bot DataBase

• /speedtest: Check the internet speed of bot server

• /serverstats: Get the stats of server

• /stats: Alias command for serverstats

• /users: Get details about the Bot Users

• /inspect: Inspect the message and give reply in json format
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
