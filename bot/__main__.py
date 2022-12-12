from bot import bot, is_logged_in, PAGE
from bot.config import OPENAI_EMAIL, OPENAI_PASSWORD
from bot.logging import LOGGER

from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, AccessTokenInvalid

def start_browser():
    PAGE.goto("https://chat.openai.com/")
    if not is_logged_in() and len(OPENAI_EMAIL and OPENAI_PASSWORD)!=0:
        print("Trying to Automate Login to OpenChat")

        PAGE.locator("button", has_text="Log in").click()
        username = PAGE.locator('input[name="username"]')
        username.fill(OPENAI_EMAIL)
        username.press("Enter")
        password = PAGE.locator('input[name="password"]')
        password.fill(OPENAI_PASSWORD)
        password.press("Enter")

        # On first login
        try:
            next_button = PAGE.locator("button", has_text="Next")
            next_button.click()
            next_button = PAGE.locator("button", has_text="Next")
            next_button.click()
            next_button = PAGE.locator("button", has_text="Done")
            next_button.click()
        except:
            pass

LOGGER(__name__).info("Client Successfully Initiated :) ")
if __name__ == "__main__":
    try:
        start_browser()
    except Exception as e:
        LOGGER(__name__).error(f"Could not start Browser for ChatGPT due to:\n{e}")
        pass
    try:
        bot.run()
    except (ApiIdInvalid, ApiIdPublishedFlood):
        raise Exception("Your API_ID/API_HASH is not valid!")
    except AccessTokenInvalid:
        raise Exception("Your BOT_TOKEN is not valid!")
