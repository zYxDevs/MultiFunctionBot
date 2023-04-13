import asyncio
import os
import shlex
import sys
import traceback
from io import BytesIO, StringIO

import aiofiles
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import *
from bot.helpers.decorators import dev_commands, ratelimit

shell_usage = f"**USAGE:** Executes terminal commands directly via bot.\n\n**Example: **<pre>/shell pip install requests</pre>"
commands = ["shell", "sh", f"shell@{BOT_USERNAME}", f"sh@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@dev_commands
@ratelimit
async def shell(client, message: Message):
    """
    Executes command in terminal via bot.
    """

    if len(message.command) < 2:
        return await message.reply_text(shell_usage, quote=True)

    user_input = message.text.split(maxsplit=1)[1]
    args = shlex.split(user_input)

    try:
        shell_replymsg = await message.reply_text("running...", quote=True)
        shell = await asyncio.create_subprocess_exec(*args, stdout=-1, stderr=-1)
        stdout, stderr = await shell.communicate()
        result = str(stdout.decode().strip()) + str(stderr.decode().strip())
    except Exception as error:
        LOGGER(__name__).warning(f"{error}")
        await shell_replymsg.edit(f"Error :-\n\n{error}")
        return

    if len(result) > 4000:
        await shell_replymsg.edit("output too large. sending it as a file..")
        file = BytesIO(result.encode())
        file.name = "output.txt"
        await shell_replymsg.reply_document(file, caption=file.name, quote=True)
    else:
        await shell_replymsg.edit(f"Output :-\n\n{result}")


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


async def py_runexec(client: Client, message: Message, replymsg: Message):
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await replymsg.edit("Executing...")
        code = message.text.split(None, 1)[1]
    except IndexError:
        return await replymsg.edit(
            "No codes found to execute.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Refresh  🔄", callback_data="refresh")]]
            ),
        )

    if "config.env" in code:
        return await replymsg.edit(
            "That's a dangerous operation! Not Permitted!",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Refresh  🔄", callback_data="refresh")]]
            ),
        )

    try:
        await aexec(code, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "success"
    final_output = f"{evaluation.strip()}"

    if len(final_output) <= 4000:
        return await replymsg.edit(
            final_output,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("refresh 🔄", callback_data="refresh")]]
            ),
        )
    async with aiofiles.open("output.txt", "w+", encoding="utf8") as file:
        await file.write(str(evaluation.strip()))

    await replymsg.edit(
        "Output too large. Sending it as a File...",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("refresh 🔄", callback_data="refresh")]]
        ),
    )
    await client.send_document(message.chat.id, "output.txt", caption="output.txt")
    os.remove("output.txt")


@Client.on_callback_query(filters.regex("refresh"))
async def botCallbacks(client, CallbackQuery):
    clicker_user_id = CallbackQuery.from_user.id
    message_user_id = CallbackQuery.message.reply_to_message.from_user.id

    if clicker_user_id != message_user_id:
        return await CallbackQuery.answer(
            "That command has not been initiated by you", show_alert=True
        )

    message = await client.get_messages(
        CallbackQuery.message.chat.id, CallbackQuery.message.reply_to_message.id
    )

    replymsg = await client.get_messages(
        CallbackQuery.message.chat.id, CallbackQuery.message.id
    )

    if CallbackQuery.data == "refresh":
        await py_runexec(client, message, replymsg)


@Client.on_message(filters.command(commands, **prefixes))
@dev_commands
@ratelimit
async def py_exec(client, message):
    """
    Executes python command via bot with refresh button.
    """
    if len(message.command) < 2:
        await message.reply_text(
            f"**Usage:** Executes python commands directly via bot.\n\n**Example: **<pre>/exec print('hello world')</pre>"
        )
    else:
        replymsg = await message.reply_text("executing..", quote=True)
        await py_runexec(client, message, replymsg)
