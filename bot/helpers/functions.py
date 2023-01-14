import os
import random
import shutil
import string

from pyrogram.enums import ChatMemberStatus, ChatType, ParseMode
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import *
from bot.logging import LOGGER

SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


async def isAdmin(message: Message) -> bool:
    """
    Return True if the message is from owner or admin of the group or sudo of the bot.
    """
    if not message.from_user:
        return False
    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.CHANNEL]:
        return False

    client = message._client
    chat_id = message.chat.id
    user_id = message.from_user.id
    check_status = await client.get_chat_member(chat_id, user_id)

    if user_id in SUDO_USERS:
        return True
    elif check_status.status in [
        ChatMemberStatus.OWNER,
        ChatMemberStatus.ADMINISTRATOR,
    ]:
        return True
    else:
        return False


async def forcesub(client, message: Message) -> bool:
    """
    Returns True if user is subscribed to Said Channel else returns False
    """
    if (
        FORCESUB_ENABLE
        and (FORCESUB_CHANNEL and FORCESUB_CHANNEL_UNAME and BOTOWNER_UNAME) is not None
        and message.chat.type
        not in [ChatType.SUPERGROUP, ChatType.CHANNEL, ChatType.GROUP, ChatType.BOT]
    ):
        try:
            user = await client.get_chat_member(FORCESUB_CHANNEL, message.chat.id)
            if user.status == "kicked":
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"<b><i>Sorry, You are banned from the Channel {FORCESUB_CHANNEL_UNAME} and hence cannot use the Bot.\nContact {BOTOWNER_UNAME}</i></b>",
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                return False
        except UserNotParticipant:
            await client.send_message(
                chat_id=message.chat.id,
                text="<b>Join the channel below to use the Bot 🔐</b>\n\n<i>Resend the command along with link after you have successfully joined...</i>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Join🔓", url=f"https://t.me/{FORCESUB_CHANNEL_UNAME}"
                            ),
                            InlineKeyboardButton(
                                "Owner🔓", url=f"https://t.me/{BOTOWNER_UNAME}"
                            ),
                        ]
                    ]
                ),
                parse_mode=ParseMode.HTML,
            )
            return False
        except Exception as err:
            await client.send_message(
                chat_id=message.chat.id,
                text=f"<i>Something went wrong in ForceSub Module\nContact {BOTOWNER_UNAME}</i>\n\n{err}",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
            return False
    return True


def get_readable_time(seconds) -> str:
    """
    Return a human-readable time format
    """

    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)

    if days != 0:
        result += f"{days}d"
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)

    if hours != 0:
        result += f"{hours}h"
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)

    if minutes != 0:
        result += f"{minutes}m"

    seconds = int(seconds)
    result += f"{seconds}s"
    return result


def get_readable_size(size):
    if not size:
        return ""
    power = 2**10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}

    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


def get_readable_file_size(size_in_bytes):
    if size_in_bytes is None:
        return "0B"
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f"{round(size_in_bytes, 2)}{SIZE_UNITS[index]}"
    except IndexError:
        return "File too large"


def speed_convert(size, byte=True):
    if not byte:
        size = size / 8
    power = 2**10
    zero = 0
    units = {0: "B/s", 1: "KB/s", 2: "MB/s", 3: "GB/s", 4: "TB/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


def get_readable_bitrate(bitrate_kbps):
    if bitrate_kbps > 10000:
        bitrate = str(round(bitrate_kbps / 1000, 2)) + " " + "Mb/s"
    else:
        bitrate = str(round(bitrate_kbps, 2)) + " " + "kb/s"

    return bitrate


def get_readable_filesize(num):
    for x in {"bytes", "KB", "MB", "GB", "TB"}:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)

        num /= 1024.0

    return "%3.1f %s" % (num, "TB")


def makedir(name: str):
    if os.path.exists(name):
        shutil.rmtree(name)
    os.mkdir(name)


def remove_N(seq):
    i = 1
    while i < len(seq):
        if seq[i] == seq[i - 1]:
            del seq[i]
            i -= 1
        else:
            i += 1


def randstr():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=7))


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d ") if days else "")
        + ((str(hours) + "h ") if hours else "")
        + ((str(minutes) + "m ") if minutes else "")
        + ((str(seconds) + "s ") if seconds else "")
        + ((str(milliseconds) + "ms ") if milliseconds else "")
    )
    return tmp[:-2]


async def multi_api():
    EMILY_API_LIST = []
    emilyapi_urls = EMILY_API_URL.split(" ")
    for api in emilyapi_urls:
        EMILY_API_LIST.append(str(api))
    return random.choice(EMILY_API_LIST)


async def api_checker():
    api_url = await multi_api()
    r = requests.get(api_url)
    if r.status_code == 200:
        LOGGER(__name__).info(f"Using API : {api_url}")
        return api_url
    else:
        await api_checker()


def url_exists(url) -> bool:
    try:
        with requests.get(url, stream=True) as response:
            try:
                response.raise_for_status()
                return True
            except requests.exceptions.HTTPError:
                return False
    except requests.exceptions.ConnectionError:
        return False
