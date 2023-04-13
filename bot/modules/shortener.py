import cloudscraper
import requests

from bot.helpers.functions import api_checker


async def bitly(url):
    dom = await api_checker()
    api = f"{dom}/shorten"
    resp = requests.get(url)
    if resp.status_code == 404:
        return "File not found/The link you entered is wrong!"
    client = cloudscraper.create_scraper(allow_brotli=False)
    try:
        resp = client.post(api, json={"type": "bitly_shorten", "url": url})
        res = resp.json()
    except BaseException:
        return "Emily API Unresponsive / Invalid Link!"
    return res["url"] if res["success"] is True else res["msg"]


async def dagd(url):
    dom = await api_checker()
    api = f"{dom}/shorten"
    resp = requests.get(url)
    if resp.status_code == 404:
        return "File not found/The link you entered is wrong!"
    client = cloudscraper.create_scraper(allow_brotli=False)
    try:
        resp = client.post(api, json={"type": "dagd_shorten", "url": url})
        res = resp.json()
    except BaseException:
        return "Emily API Unresponsive / Invalid Link!"
    return res["url"] if res["success"] is True else res["msg"]


async def tinyurl(url):
    dom = await api_checker()
    api = f"{dom}/shorten"
    resp = requests.get(url)
    if resp.status_code == 404:
        return "File not found/The link you entered is wrong!"
    client = cloudscraper.create_scraper(allow_brotli=False)
    try:
        resp = client.post(api, json={"type": "tinyurl_shorten", "url": url})
        res = resp.json()
    except BaseException:
        return "Emily API Unresponsive / Invalid Link!"
    return res["url"] if res["success"] is True else res["msg"]


async def osdb(url):
    dom = await api_checker()
    api = f"{dom}/shorten"
    resp = requests.get(url)
    if resp.status_code == 404:
        return "File not found/The link you entered is wrong!"
    client = cloudscraper.create_scraper(allow_brotli=False)
    try:
        resp = client.post(api, json={"type": "osdb_shorten", "url": url})
        res = resp.json()
    except BaseException:
        return "Emily API Unresponsive / Invalid Link!"
    return res["url"] if res["success"] is True else res["msg"]


async def ttm(url):
    dom = await api_checker()
    api = f"{dom}/shorten"
    resp = requests.get(url)
    if resp.status_code == 404:
        return "File not found/The link you entered is wrong!"
    client = cloudscraper.create_scraper(allow_brotli=False)
    try:
        resp = client.post(api, json={"type": "ttm_shorten", "url": url})
        res = resp.json()
    except BaseException:
        return "Emily API Unresponsive / Invalid Link!"
    return res["url"] if res["success"] is True else res["msg"]


async def isgd(url):
    dom = await api_checker()
    api = f"{dom}/shorten"
    resp = requests.get(url)
    if resp.status_code == 404:
        return "File not found/The link you entered is wrong!"
    client = cloudscraper.create_scraper(allow_brotli=False)
    try:
        resp = client.post(api, json={"type": "isgd_shorten", "url": url})
        res = resp.json()
    except BaseException:
        return "Emily API Unresponsive / Invalid Link!"
    return res["url"] if res["success"] is True else res["msg"]


async def vgd(url):
    dom = await api_checker()
    api = f"{dom}/shorten"
    resp = requests.get(url)
    if resp.status_code == 404:
        return "File not found/The link you entered is wrong!"
    client = cloudscraper.create_scraper(allow_brotli=False)
    try:
        resp = client.post(api, json={"type": "vgd_shorten", "url": url})
        res = resp.json()
    except BaseException:
        return "Emily API Unresponsive / Invalid Link!"
    return res["url"] if res["success"] is True else res["msg"]


async def clickru(url):
    dom = await api_checker()
    api = f"{dom}/shorten"
    resp = requests.get(url)
    if resp.status_code == 404:
        return "File not found/The link you entered is wrong!"
    client = cloudscraper.create_scraper(allow_brotli=False)
    try:
        resp = client.post(api, json={"type": "clckru_shorten", "url": url})
        res = resp.json()
    except BaseException:
        return "Emily API Unresponsive / Invalid Link!"
    return res["url"] if res["success"] is True else res["msg"]


async def clilp(url):
    dom = await api_checker()
    api = f"{dom}/shorten"
    resp = requests.get(url)
    if resp.status_code == 404:
        return "File not found/The link you entered is wrong!"
    client = cloudscraper.create_scraper(allow_brotli=False)
    try:
        resp = client.post(api, json={"type": "clilp_shorten", "url": url})
        res = resp.json()
    except BaseException:
        return "Emily API Unresponsive / Invalid Link!"
    return res["url"] if res["success"] is True else res["msg"]
