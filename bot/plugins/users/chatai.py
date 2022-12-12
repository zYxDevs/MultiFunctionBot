"""Make some requests to OpenAI's chatbot"""

from pyrogram import Client, enums, filters
from pyrogram.types import Message
from telegram.helpers import escape_markdown

from bot import BOT_USERNAME, PAGE, send_message_to_browser
from bot.config import DATABASE_URL, LOG_CHANNEL, prefixes
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import sudo_commands, user_commands
from bot.helpers.functions import forcesub
from bot.logging import LOGGER


def get_last_message():
    """Get the latest response from OpenAI`s ChatGPT"""
    page_elements = PAGE.query_selector_all("div[class*='request-']")
    last_element = page_elements[-1]
    prose = last_element
    try:
        code_blocks = prose.query_selector_all("pre")
    except Exception as e:
        response = f"Server probably disconnected, try running /reload\nERROR: {e}"
        return response
    if len(code_blocks) > 0:
        # get all children of prose and add them one by one to respons
        response = ""
        for child in prose.query_selector_all("p,pre"):
            LOGGER(__name__).info(child.get_property("tagName"))
            if str(child.get_property("tagName")) == "PRE":
                code_container = child.query_selector("code")
                response += f"\n```\n{escape_markdown(code_container.inner_text(), version=2)}\n```"
            else:
                # replace all <code>x</code> things with `x`
                text = child.inner_html()
                response += escape_markdown(text, version=2)
        response = response.replace("<code\>", "`")
        response = response.replace("</code\>", "`")
    else:
        response = escape_markdown(prose.inner_text(), version=2)
    return response


@Client.on_message(
    filters.command(["reload_browser", f"reload_browser@{BOT_USERNAME}"], **prefixes)
)
@sudo_commands
async def reload_browser(_, message: Message):
    """Reload the Browser to refresh the OpenAI`s Website"""
    user_id = message.from_user.id
    LOGGER(__name__).info(f"Got a reload command from user {user_id}")
    PAGE.reload()
    await message.reply_text("Reloaded the browser!")
    await message.reply_text("Let's check if it's working!")


@Client.on_message(filters.command(["chatai", f"chatai@{BOT_USERNAME}"], **prefixes))
@user_commands
async def chatgpt(client, message: Message):
    """Send a query to OpenAI`s ChatGPT to generate AI results"""
    query = None

    fsub = await forcesub(client, message)
    if not fsub:
        return

    reply_to = message.reply_to_message

    if len(message.command) > 1:
        query = message.text.split(None, 1)[1]
    elif reply_to is not None:
        query = reply_to.text
    elif len(message.command) < 2 or reply_to is None:
        err = "<b><i>Please send a query or reply to an query to proceed!</i></b>"
        await message.reply_text(text=err, disable_web_page_preview=True, quote=True)
        return

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
        import datetime

        if last_used_on != datetime.date.today().isoformat():
            await DatabaseHelper().update_last_used_on(user_id)

    if query is not None:
        send_message_to_browser(query)
        response = get_last_message()
        await message.reply_text(
            text=response, disable_web_page_preview=True, quote=True
        )
    else:
        await message.reply_text(
            text="Encountered some error while parsing ChatGPT Query!",
            disable_web_page_preview=True,
            quote=True,
        )
