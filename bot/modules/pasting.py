import cloudscraper
import httpx
from bs4 import BeautifulSoup

from bot.helpers.functions import api_checker


async def telegraph_paste(res):
    dom = await api_checker()
    api = f"{dom}/paste"
    client = cloudscraper.create_scraper(allow_brotli=False)
    try:
        resp = client.post(api, json={"type": "telegraph_paste", "text": res})
        res = resp.json()
    except BaseException:
        return "API UnResponsive / Invalid Link!"
    if res["success"] is True:
        return res["url"]
    else:
        return res["msg"]


async def katbin_paste(text: str) -> str:
    katbin_url = "https://katb.in"
    client = httpx.AsyncClient()
    response = await client.get(katbin_url)
    soup = BeautifulSoup(response.content, "html.parser")
    csrf_token = soup.find("input", {"name": "_csrf_token"}).get("value")
    try:
        paste_post = await client.post(
            katbin_url,
            data={"_csrf_token": csrf_token, "paste[content]": text},
            follow_redirects=False,
        )
        output_url = f"{katbin_url}{paste_post.headers['location']}"
        await client.aclose()
        return output_url
    except BaseException:
        return "Something went wrong while pasting text to katb.in "
