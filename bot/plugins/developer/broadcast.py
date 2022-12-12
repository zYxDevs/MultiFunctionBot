import asyncio
import datetime
import os
import random
import string
import time
import traceback

import aiofiles
from pyrogram import Client, filters
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    UserIsBlocked,
)

from bot.config import BOT_USERNAME, prefixes
from bot.helpers.database import DatabaseHelper
from bot.helpers.decorators import dev_commands

Broadcast_IDs = {}

commands = ["broadcast", f"broadcast@{BOT_USERNAME}"]


@Client.on_message(filters.command(commands, **prefixes))
@dev_commands
async def broadcast(c, m):
    out = await m.reply_text(
        text=f"Broadcast initiated! You will be notified with log file when all the users are notified."
    )
    all_users = await DatabaseHelper().get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = "".join([random.choice(string.ascii_letters) for i in range(3)])
        if not Broadcast_IDs.get(broadcast_id):
            break
    start_time = time.time()
    total_users = await DatabaseHelper().total_users_count()
    done = 0
    failed = 0
    success = 0
    Broadcast_IDs[broadcast_id] = dict(
        total=total_users, current=done, failed=failed, success=success
    )
    async with aiofiles.open("broadcast.txt", "w") as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(user_id=int(user["id"]), message=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await DatabaseHelper().delete_user(user["id"])
            done += 1
            if Broadcast_IDs.get(broadcast_id) is None:
                break
            else:
                Broadcast_IDs[broadcast_id].update(
                    dict(current=done, failed=failed, success=success)
                )
    if Broadcast_IDs.get(broadcast_id):
        Broadcast_IDs.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(
            text=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True,
        )
    else:
        await m.reply_document(
            document="broadcast.txt",
            caption=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True,
        )

    try:
        os.remove("broadcast.txt")
    except BaseException:
        pass


async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception:
        return 500, f"{user_id} : {traceback.format_exc()}\n"
