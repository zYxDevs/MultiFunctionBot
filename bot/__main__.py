from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, AccessTokenInvalid

from bot import bot
from bot.logging import LOGGER

LOGGER(__name__).info("Client Successfully Initiated :) ")
if __name__ == "__main__":
    try:
        bot.run()
    except (ApiIdInvalid, ApiIdPublishedFlood):
        raise Exception("Your API_ID/API_HASH is not valid!")
    except AccessTokenInvalid:
        raise Exception("Your BOT_TOKEN is not valid!")
