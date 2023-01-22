import math
import time

from bot.helpers.functions import TimeFormatter, get_readable_size


async def progress(
    current,
    total,
    progressMessage,
    fileName,
    start,
):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "\n[{0}{1}] \n<b>Progress:</b> {2}%\n".format(
            "".join(["●" for _ in range(math.floor(percentage / 8))]),
            "".join(["○" for _ in range(20 - math.floor(percentage / 8))]),
            round(percentage, 2),
        )

        tmp = progress + "{0} of {1}\n<b>Speed:</b> {2}/s\n<b>ETA:</b> {3}\n".format(
            get_readable_size(current),
            get_readable_size(total),
            get_readable_size(speed),
            estimated_total_time if estimated_total_time != "" else "0 s",
        )
        try:
            await progressMessage.edit(text=f"Downloading: `{fileName}` \n {tmp}")
        except BaseException:
            pass
