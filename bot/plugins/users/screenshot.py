import asyncio
import datetime
import json
import re
import shlex
import subprocess
import time
from urllib.parse import unquote

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from requests_toolbelt import MultipartEncoder

from bot.helpers.decorators import ratelimit, user_commands
from bot.helpers.functions import *
from bot.helpers.functions import randstr
from bot.modules.regex import is_a_url


async def slowpics_collection(message, file_name, path):
    """
    Uploads image(s) to https://slow.pics/ from a specified directory.
    """

    msg = await message.reply_text(
        "uploading generated screenshots to slow.pics.", quote=True
    )

    img_list = os.listdir(path)
    data = {
        "collectionName": f"{unquote(file_name)}",
        "hentai": "false",
        "optimizeImages": "false",
        "public": "false",
    }

    for i in range(len(img_list)):
        data[f"images[{i}].name"] = img_list[i]
        data[f"images[{i}].file"] = (
            img_list[i],
            open(f"{path}/{img_list[i]}", "rb"),
            "image/png",
        )

    with requests.Session() as client:
        client.get("https://slow.pics/api/collection")
        files = MultipartEncoder(data)
        length = str(files.len)

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Length": length,
            "Content-Type": files.content_type,
            "Origin": "https://slow.pics/",
            "Referer": "https://slow.pics/collection",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
            "X-XSRF-TOKEN": client.cookies.get_dict()["XSRF-TOKEN"],
        }

        response = client.post(
            "https://slow.pics/api/collection", data=files, headers=headers
        )
        await msg.edit(
            f"File Name: `{unquote(file_name)}`\n\nFrames: https://slow.pics/c/{response.text}",
            disable_web_page_preview=True,
        )


async def generate_ss_from_file(
    message, replymsg, file_name, frame_count, file_duration
):
    """
    Generates screenshots from partially/fully downloaded files using ffmpeg.
    """

    await replymsg.edit(
        f"Generating **{frame_count}** screnshots from `{unquote(file_name)}`, please wait..."
    )

    rand_str = randstr()
    makedir(f"screenshot_{rand_str}")

    loop_count = frame_count
    while loop_count != 0:

        random_timestamp = random.uniform(1, file_duration)
        timestamp = str(datetime.timedelta(seconds=int(random_timestamp)))
        outputpath = f"screenshot_{rand_str}/{(frame_count - loop_count) + 1}.png"

        ffmpeg_command = (
            f"ffmpeg -y -ss {timestamp} -i '{file_name}' -vframes 1 {outputpath}"
        )
        args = shlex.split(ffmpeg_command)

        shell = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await shell.communicate()
        result = str(stdout.decode().strip()) + str(stderr.decode().strip())

        if "File ended prematurely" in result:
            loop_count += 1
        loop_count -= 1

    await replymsg.delete()
    await slowpics_collection(
        message, file_name, path=f"{os.getcwd()}/screenshot_{rand_str}"
    )

    shutil.rmtree(f"screenshot_{rand_str}")
    os.remove(file_name)


async def generate_ss_from_link(
    message, replymsg, file_url, headers, file_name, frame_count, file_duration
):
    """
    Generates screenshots from direct download links using ffmpeg.
    """

    await replymsg.edit(
        f"Generating **{frame_count}** screnshots from `{unquote(file_name)}`, please wait..."
    )

    rand_str = randstr()
    makedir(f"screenshot_{rand_str}")

    loop_count = frame_count
    while loop_count != 0:
        random_timestamp = random.uniform(1, file_duration)
        timestamp = str(datetime.timedelta(seconds=int(random_timestamp)))
        outputpath = f"screenshot_{rand_str}/{(frame_count - loop_count) + 1}.png"

        ffmpeg_command = f"ffmpeg -headers '{headers}' -y -ss {timestamp} -i {file_url} -vframes 1 {outputpath}"
        args = shlex.split(ffmpeg_command)

        shell = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await shell.communicate()
        str(stdout.decode().strip()) + str(stderr.decode().strip())

        loop_count -= 1
        time.sleep(3)

    await replymsg.delete()
    await slowpics_collection(
        message, file_name, path=f"{os.getcwd()}/screenshot_{rand_str}"
    )

    shutil.rmtree(f"screenshot_{rand_str}")


async def ddl_screenshot(message, frame_count, url):
    """
    Generates Screenshots from Direct Download links.
    """

    replymsg = await message.reply_text(
        "**Checking direct download url....**", quote=True
    )

    try:

        file_url = f"'{url}'"
        file_name = re.search(".+/(.+)", url)[1]

        total_duration = subprocess.check_output(
            f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {file_url}",
            shell=True,
        ).decode("utf-8")
        total_duration = float(total_duration.strip())

        headers = "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4136.7 Safari/537.36"

        await generate_ss_from_link(
            message,
            replymsg,
            file_url,
            headers,
            file_name,
            frame_count,
            file_duration=total_duration,
        )

    except MessageNotModified:
        pass
    except Exception:
        return await replymsg.edit(
            "Something went wrong with the given url. Make sure that url is downloadable video file wich is non ip specific and should return proper response code without any required headers"
        )


async def telegram_screenshot(client, message, frame_count):
    """
    Generates Screenshots from Telegram Video Files.
    """

    message = message.reply_to_message
    if message.text:
        return await message.reply_text(
            "Reply to a proper video file to Generate Screenshots. **", quote=True
        )

    elif message.media.value == "video":
        media = message.video

    elif message.media.value == "document":
        media = message.document

    else:
        return await message.reply_text(
            "can only generate screenshots from video file....", quote=True
        )

    file_name = str(media.file_name)
    mime = media.mime_type
    size = media.file_size

    if message.media.value == "document" and "video" not in mime:
        return await message.reply_text(
            "can only generate screenshots from video file....", quote=True
        )

    # Dowloading partial file.
    replymsg = await message.reply_text(
        "Downloading partial video file....", quote=True
    )

    if int(size) <= 200000000:
        await message.download(os.path.join(os.getcwd(), file_name))
        downloaded_percentage = 100  # (100% download)

    else:
        limit = ((25 * size) / 100) / 1000000
        async for chunk in client.stream_media(message, limit=int(limit)):
            with open(file_name, "ab") as file:
                file.write(chunk)

        downloaded_percentage = 25

    await replymsg.edit("Partial file downloaded....")

    mediainfo_json = json.loads(
        subprocess.check_output(["mediainfo", file_name, "--Output=JSON"]).decode(
            "utf-8"
        )
    )
    total_duration = mediainfo_json["media"]["track"][0]["Duration"]

    if downloaded_percentage == 100:
        partial_file_duration = float(total_duration)
    else:
        partial_file_duration = (downloaded_percentage * float(total_duration)) / 100

    await generate_ss_from_file(
        message, replymsg, file_name, frame_count, file_duration=partial_file_duration
    )


mediainfo_usage = (
    "Generates video frame screenshot from Telegram files or direct download links."
)
commands = ["screenshot", "ss"]


@Client.on_message(filters.command(commands, **prefixes))
@user_commands
@ratelimit
async def screenshot(client, message: Message):
    replied_message = message.reply_to_message
    if replied_message:
        try:
            user_input = message.text.split(None, 1)[1]
            frame_count = int(user_input.strip())
        except BaseException:
            frame_count = 5

        frame_count = min(frame_count, 15)
        return await telegram_screenshot(client, message, frame_count)

    if len(message.command) < 2:
        return await message.reply_text(mediainfo_usage, quote=True)

    user_input = message.text.split(None, 1)[1]
    if "|" in user_input:

        frame_count = user_input.split("|")[-1].strip()
        url = user_input.split("|")[0].strip()

        try:
            frame_count = int(frame_count)
        except BaseException:
            frame_count = 5
        frame_count = min(frame_count, 15)
    else:
        frame_count = 5
        url = user_input.split("|")[0].strip()

    if is_ddl := is_a_url(url):
        return await ddl_screenshot(message, frame_count, url)
    else:
        return await message.reply_text(
            "This type of URL is not supported!", quote=True
        )
