import asyncio
import json
import os
import re
import urllib.parse
from http.cookiejar import MozillaCookieJar
from time import sleep

import chromedriver_autoinstaller
import cloudscraper
import httpx
from bs4 import BeautifulSoup
from lk21 import Bypass
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from zippyshare_downloader import extract_info as zippy_info

from bot.config import *
from bot.helpers.functions import url_exists
from bot.modules.regex import is_sendcm_folder_link


async def androiddatahost(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            c = BeautifulSoup(response.content, "html.parser")
            fin = c.find("div", {"download2"})
            dl_url = fin.find("a")["href"].replace(" ", "%20")
            return dl_url
        except BaseException:
            return "Some Error Occurred \nCould not generate dl-link for your URL"


async def anonfiles(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            if dlurl := soup.find(id="download-url"):
                return dlurl["href"]
        except BaseException:
            return "Could not Generate Direct Link for your AnonFiles Link :("


async def antfiles(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            parsed_url = urllib.parse.urlparse(url)
            if a := soup.find(class_="main-btn", href=True):
                final_url = "{0.scheme}://{0.netloc}/{1}".format(parsed_url, a["href"])
                return final_url
        except BaseException:
            return "Could not Generate Direct Link for your AntFiles Link :("


async def artstation(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    url = url.split("/")[-1]
    h = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    apix = f"https://www.artstation.com/projects/{url}.json"
    await asyncio.sleep(2)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(apix, headers=h)
            uhh = response.json()
            dl_url = uhh["assets"][0]["image_url"]
            return dl_url
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def bunkr_cyber(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    count = 1
    dl_msg = ""
    resp = requests.get(url)
    if resp.status_code == 404:
        return "File not found/The link you entered is wrong!"
    link_type = "Bunkr" if "bunkr.is" in url else "CyberDrop"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            if link_type == "Bunkr":
                if "stream.bunkr.is" in url:
                    return url.replace("stream.bunkr.is/v", "media-files.bunkr.is")
                json_data_element = soup.find("script", {"id": "__NEXT_DATA__"})
                json_data = json.loads(json_data_element.string)
                files = json_data["props"]["pageProps"]["files"]
                for file in files:
                    item_url = "https://media-files.bunkr.is/" + file["name"]
                    item_url = item_url.replace(" ", "%20")
                    dl_msg += f"<b>{count}.</b> <code>{item_url}</code><br>"
                    count += 1
            else:
                items = soup.find_all("a", {"class": "image"})
                for item in items:
                    item_url = item["href"]
                    item_url = item_url.replace(" ", "%20")
                    dl_msg += f"<b>{count}.</b> <code>{item_url}</code><br>"
                    count += 1
            fld_msg = f"Your provided {link_type} link is of Folder and I've Found {count - 1} files in the Folder."
            fld_msg += f"I've generated Direct Links for all the files.<br><br>"
            return fld_msg + dl_msg
        except BaseException:
            return f"Could not Generate Direct Link for your {link_type} Link :("


async def dropbox(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    if "dropbox.com/s/" in url:
        return url.replace("dropbox.com", "dl.dropboxusercontent.com")
    else:
        return url.replace("?dl=0", "?dl=1")


async def fembed(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    try:
        url = url[:-1] if url[-1] == "/" else url
        TOKEN = url.split("/")[-1]
        API = "https://fembed-hd.com/api/source/"
        async with httpx.AsyncClient() as client:
            response = await client.post(API + TOKEN)
            dl_url = response.json()["data"].replace(" ", "%20")
            return dl_url
    except BaseException:
        return "Could not Generate Direct Link for your FEmbed Link :("


async def fichier(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url)
            if response.status_code == 404:
                return "File not found/The link you entered is wrong!"
            soup = BeautifulSoup(response.content, "lxml")
            if soup.find("a", {"class": "ok btn-general btn-orange"}) is not None:
                dl_url = soup.find("a", {"class": "ok btn-general btn-orange"})["href"]
                if dl_url is None:
                    return "Unable to generate Direct Link for 1fichier!"
                else:
                    return dl_url
            elif len(soup.find_all("div", {"class": "ct_warn"})) == 3:
                str_2 = soup.find_all("div", {"class": "ct_warn"})[-1]
                if "you must wait" in str(str_2).lower():
                    numbers = [
                        int(word) for word in str(str_2).split() if word.isdigit()
                    ]
                    if not numbers:
                        return "1fichier is on a limit. Please wait a few minutes/hour."
                    else:
                        return (
                            f"1fichier is on a limit. Please wait {numbers[0]} minute."
                        )
                elif "protect access" in str(str_2).lower():
                    return f"This link requires a password!\n\n<b>This link requires a password!</b>"
                else:
                    print(str_2)
                    return "Error trying to generate Direct Link from 1fichier!"
            elif len(soup.find_all("div", {"class": "ct_warn"})) == 4:
                str_1 = soup.find_all("div", {"class": "ct_warn"})[-2]
                str_3 = soup.find_all("div", {"class": "ct_warn"})[-1]
                if "you must wait" in str(str_1).lower():
                    numbers = [
                        int(word) for word in str(str_1).split() if word.isdigit()
                    ]
                    if not numbers:
                        return "1fichier is on a limit. Please wait a few minutes/hour."
                    else:
                        return (
                            f"1fichier is on a limit. Please wait {numbers[0]} minute."
                        )
                elif "bad password" in str(str_3).lower():
                    return "The password you entered is wrong!"
                else:
                    return "Error trying to generate Direct Link from 1fichier!"
            else:
                return "Error trying to generate Direct Link from 1fichier!"
        except httpx.HTTPError as e:
            return "Error trying to generate Direct Link from 1fichier!"


async def filesIm(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    try:
        return Bypass().bypass_filesIm(url)
    except BaseException:
        return "Could not Generate Direct Link for your FilesIm Link :("


async def gdbot(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = cloudscraper.create_scraper(allow_brotli=False)
    try:
        with httpx.AsyncClient() as client:
            resp = await client.get(url)
            gdtot_url = re.findall('mb-2" href="(.*?)" target="_blank"', resp.text)
            url = gdtot_url[0]
            resp = await client.get(url)
            token = re.findall("'token', '(.*?)'", resp.text)[0]
            data = {"token": token}
            resp2 = await client.post(url, data=data).text
            res = resp2.split('":"')[1].split('"}')[0].replace("\\", "")
            return res
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def github(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    try:
        async with httpx.AsyncClient() as client:
            async with client.get(url) as response:
                return response.headers["location"]
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def gofile(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    api_uri = "https://api.gofile.io"
    try:
        async with httpx.AsyncClient() as client:
            async with client.get(f"{api_uri}/createAccount") as response:
                res = response.json()
                data = {
                    "contentId": url.split("/")[-1],
                    "token": res["data"]["token"],
                    "websiteToken": 12345,
                    "cache": "true",
                }
                async with client.get(f"{api_uri}/getContent", params=data) as response:
                    res = response.json()
                    for item in res["data"]["contents"].values():
                        content = item
                        dl_url = content["directLink"]
                        dl_url = dl_url.replace(" ", "%20")
                        return dl_url
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def hubcloud(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"

    chromedriver_autoinstaller.install()

    # Specifying Buttons
    btnshow = '//*[@id="btnshow"]/a/h4'
    verify_button2 = '//*[@id="verify_button2"]'
    verify_button = '//*[@id="verify_button"]'
    two_steps_btn = '//a[@class="rdr_btn block"]'
    workers = "/html/body/center/div[2]/div[1]/h2/a[1]"
    bgsora = '//*[@id="bgsora"]'

    # Selenium Set-Up
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Scrapping
    wd = webdriver.Chrome(options=chrome_options)
    wd.get(url)
    try:
        WebDriverWait(wd, 8).until(
            ec.element_to_be_clickable((By.XPATH, bgsora))
        ).click()
    except TimeoutException:
        sleep(3)
        WebDriverWait(wd, 12).until(
            ec.element_to_be_clickable((By.XPATH, bgsora))
        ).click()
    sleep(8)
    flink = wd.current_url
    pattern1 = re.compile(r"\bhttps?://.*(hubcloud)\S+", re.IGNORECASE)
    pattern2 = re.compile(r"\bhttps?://.*(newsongs)\S+", re.IGNORECASE)
    pattern3 = re.compile(r"\bhttps?://.*(hashhackers)\S+", re.IGNORECASE)
    if pattern1.match(flink):
        sleep(4)
        final_msg = wd.find_element(By.XPATH, workers).get_attribute("href")
    elif pattern2.match(flink) or pattern3.match(flink):
        WebDriverWait(wd, 20).until(
            ec.element_to_be_clickable((By.XPATH, btnshow))
        ).click()
        WebDriverWait(wd, 20).until(
            ec.element_to_be_clickable((By.XPATH, verify_button2))
        ).click()
        WebDriverWait(wd, 17).until(
            ec.element_to_be_clickable((By.XPATH, verify_button))
        ).click()
        sleep(17)
        lastbutton = wd.find_element(By.XPATH, two_steps_btn)
        wd.execute_script("arguments[0].click();", lastbutton)
        sleep(5)
        wd.current_window_handle
        try:
            Itab = wd.window_handles[1]
        except IndexError:
            IItab = wd.window_handles[0]
        try:
            wd.switch_to.window(Itab)
        except IndexError:
            wd.switch_to.window(IItab)
        final_msg = wd.find_element(By.XPATH, workers).get_attribute("href")
    else:
        final_msg = "Could not any matching Links to Bypass from the Link!"
    return final_msg


async def hxfile(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    try:
        url = url[:-1] if url[-1] == "/" else url
        token = url.split("/")[-1]
        async with httpx.AsyncClient() as client:
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            }
            data = {
                "op": "download2",
                "id": token,
                "rand": "",
                "referer": "",
                "method_free": "",
                "method_premium": "",
            }
            async with client.post(url, headers=headers, data=data) as response:
                soup = BeautifulSoup(response.text, "html.parser")
                if btn := soup.find(class_="btn btn-dow"):
                    return btn["href"]
                if unique := soup.find(id="uniqueExpirylink"):
                    return unique["href"]
    except BaseException:
        return "Could not Generate Direct Link for your HXFile Link :("


async def krakenfiles(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url)
            soup = BeautifulSoup(resp.text, "lxml")
            token = soup.find("input", id="dl-token")["value"]
            items = soup.find_all("div", attrs={"data-file-hash": True})
            hashes = [item["data-file-hash"] for item in items]
            if not hashes:
                return f"KrakenFiles: Hash not found for : {url}"
            dl_hash = hashes[0]
            payload = (
                f'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="token"\r\n\r\n'
                f"{token}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
            )
            headers = {
                "content-type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
                "cache-control": "no-cache",
                "hash": dl_hash,
            }
            dl_link_resp = await client.post(
                f"https://krakenfiles.com/download/{hash}",
                data=payload,
                headers=headers,
            )
            dl_link_json = dl_link_resp.json()
            dl_url = dl_link_json["url"].replace(" ", "%20")
            return dl_url
        except BaseException:
            return "Some Error Occurred \nCould not generate dl-link for your URL"


async def letsupload(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    try:
        return Bypass().bypass_url(url)
    except BaseException:
        return "Could not Generate Direct Link for your LetsUpload Link :("


async def linkpoi(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    try:
        return Bypass().bypass_linkpoi(url)
    except BaseException:
        return "Could not Generate Direct Link for your Linkpoi Link :("


async def mdisk(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    token = url.split("/")[-1]
    async with httpx.AsyncClient() as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        }
        f_url = f"https://diskuploader.entertainvideo.com/v1/file/cdnurl?param={token}"
        try:
            response = await client.get(f_url, headers=headers)
            dl_url = response.json()["download"].replace(" ", "%20")
            return dl_url
        except BaseException:
            return "Some Error Occurred \nCould not generate dl-link for your URL"


async def mdisk_mpd(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    token = url.split("/")[-1]
    async with httpx.AsyncClient() as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        }
        f_url = f"https://diskuploader.entertainvideo.com/v1/file/cdnurl?param={token}"
        try:
            response = await client.get(f_url, headers=headers)
            dl_url = response.json()["source"].replace(" ", "%20")
            return dl_url
        except BaseException:
            return "Some Error Occurred \nCould not generate dl-link for your URL"


async def mediafire(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url)
            page = BeautifulSoup(resp.content, "lxml")
            info = page.find("a", {"aria-label": "Download file"})
            dl_url = info.get("href").replace(" ", "%20")
            return dl_url
        except BaseException:
            return "Some Error Occurred \nCould not generate dl-link for your URL"


async def megaup(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = cloudscraper.create_scraper(allow_brotli=False)
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url)
            data = (
                resp.text.split("DeObfuscate_String_and_Create_Form_With_Mhoa_URL(", 2)[
                    2
                ]
                .split(");")[0]
                .split(",")
            )
            data = [a.strip("' ") for a in data]
            idurl = "".join(data[0][i] for i in range(len(data[0]) // 4 - 1, -1, -1))
            for i in range(
                int(len(data[0]) / 4 * 3 - 1), int(len(data[0]) / 4 * 2) - 1, -1
            ):
                idurl += data[0][i]
            for i in range(int((len(data[1]) - 3) / 2 + 2), 2, -1):
                idurl += data[1][i]
            des_url = f"https://download.megaup.net/?idurl={idurl}&idfilename={data[2]}&idfilesize={data[3]}".replace(
                " ", "%20"
            )
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not generate dl-link for your URL"


async def mirrored(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    res_msg = None
    url = url + "/" if url[-1] != "/" else url
    hs = {
        "Connection": "Keep-Alive",
        "Content-Type": "text/html; charset=UTF-8",
        "Keep-Alive": "timeout=30, max=2500",
        "Server": "Apache",
        "Vary": "Accept-Encoding",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    }
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, headers=hs)
            soup = BeautifulSoup(res.text, "html.parser")
            x = soup.select('link[href^="https://www.mirrored.to/files"]')
            res2 = await client.get(x)
            soup2 = BeautifulSoup(res2.content, "html.parser")
            y = soup2.select('link[href^="/getlink/"]')
            res_msg = ""
            for _ in y:
                res_msg += f"{_}"
            return res_msg
        except BaseException:
            return "Could not Generate Direct Link for your Mirrored Link :("


async def mp4upload(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    url = url[:-1] if url[-1] == "/" else url
    headers = {"referer": "https://mp4upload.com"}
    token = url.split("/")[-1]
    data = {
        "op": "download2",
        "id": token,
        "rand": "",
        "referer": "https://www.mp4upload.com/",
        "method_free": "",
        "method_premium": "",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, data=data)
            des_url = response.headers["Location"]
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not generate dl-link for your URL"


async def osdn(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    link = re.findall(r"\bhttps?://.*osdn\.net\S+", url)[0]
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(link, allow_redirects=True)
            page = BeautifulSoup(response.content, "lxml")
            info = page.find("a", {"class": "mirror_link"})
            link = urllib.parse.unquote("https://osdn.net" + info["href"])
            mirrors = page.find("form", {"id": "mirror-select-form"}).findAll("tr")
            urls = []
            for data in mirrors[1:]:
                mirror = data.find("input")["value"]
                urls.append(re.sub(r"m=(.*)&f", f"m={mirror}&f", link))
            await asyncio.sleep(0.5)
            return urls[0]
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def pandafile(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    id_p = re.compile("pandafiles.com/(.+?)/")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://pandafiles.com",
        "Referer": "https://pandafiles.com/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Te": "trailers",
    }
    id = re.findall(id_p, url)[0]
    data = {
        "op": "download2",
        "usr_login": "",
        "id": id,
        "rand": "",
        "referer": url,
        "method_free": "Free Download",
        "method_premium": "",
        "adblock_detected": "0",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            bsObj = BeautifulSoup(response.content, features="lxml")
            for a in bsObj.find_all("a", href=True):
                dl_url = a["href"].replace(" ", "%20")
                await asyncio.sleep(0.5)
                return dl_url
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def pixeldrain(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    url = url.strip("/ ")
    file_id = url.split("/")[-1]
    if url.split("/")[-2] == "l":
        info_link = f"https://pixeldrain.com/api/list/{file_id}"
        dl_link = f"{info_link}/zip"
    else:
        dl_link = f"https://pixeldrain.com/api/file/{file_id}"
    dl_link = dl_link.replace(" ", "%20")
    await asyncio.sleep(0.5)
    return dl_link


async def pixl(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    resp = requests.get(url)
    if resp.status_code == 404:
        return "File not found/The link you entered is wrong!"
    try:
        currentpage = 1
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            thmbnailanchors = soup.findAll(attrs={"class": "--media"})
            links = soup.findAll(attrs={"data-pagination": "next"})
            try:
                url = links[0].attrs["href"]
            except BaseException:
                url = None
            count = 1
            ddl_msg = ""
            for ref in thmbnailanchors:
                imgdata = await client.get(ref.attrs["href"])
                if not imgdata.status_code == 200:
                    await asyncio.sleep(3)
                    continue
                imghtml = BeautifulSoup(imgdata.text, "html.parser")
                downloadanch = imghtml.find(attrs={"class": "btn-download"})
                currentimg = downloadanch.attrs["href"]
                ddl_msg += f"<b>{count}.</b> <code>{currentimg}</code><br>"
                count += 1
            currentpage += 1
            fld_msg = f"Your provided Pixl.is link is of Folder and I've Found {count - 1} files in the folder.<br>"
            fld_msg += f"I've generated Direct Links for all the files.<br><br>"
            return fld_msg + ddl_msg
    except BaseException:
        return "Could not Generate Direct Link for your Pixl.is Link :("


async def sbembed(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    dl_url = None
    try:
        f_url = Bypass().bypass_sbembed(url)
        count = len(f_url)
        lst_link = [f_url[i] for i in f_url]
        dl_url += lst_link[count - 1]
        return dl_url
    except BaseException:
        return "Could not Generate Direct Link for your SBEmbed Link :("


async def sendcm(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"

    res = requests.get(url)
    if res.status_code == 404:
        return "File not found/The link you entered is wrong!"
    base_url = "https://send.cm/"
    client = cloudscraper.create_scraper(allow_brotli=False)
    hs = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    }
    is_sendcm_folder = is_sendcm_folder_link(url)
    if is_sendcm_folder:
        done = False
        msg = ""
        page_no = 0
        async with httpx.AsyncClient() as client:
            while not done:
                page_no += 1
                response = await client.get(url)
                soup = BeautifulSoup(response.content, "lxml")
                table = soup.find("table", id="xfiles")
                files = table.find_all("a", class_="tx-dark")
                for file in files:
                    file_url = file["href"]
                    response2 = await client.get(file_url)
                    scrape = BeautifulSoup(response2.text, "html.parser")
                    inputs = scrape.find_all("input")
                    file_id = inputs[1]["value"]
                    file_name = re.findall("URL=(.*?) - ", response2.text)[0].split(
                        "]"
                    )[1]
                    parse = {"op": "download2", "id": file_id, "referer": url}
                    response3 = await client.post(base_url, data=parse, headers=hs)
                    dl_url = response3.headers["Location"]
                    dl_url = dl_url.replace(" ", "%20")
                    msg += f"File Name: {file_name}<br>File Link: {file_url}<br>Download Link: {dl_url}<br>"
                    pages = soup.find("ul", class_="pagination")
                    if pages is None:
                        done = True
                    else:
                        current_page = pages.find(
                            "li", "page-item actived", recursive=False
                        )
                        next_page = current_page.next_sibling
                        if next_page is None:
                            done = True
                        else:
                            url = base_url + next_page["href"]
                await asyncio.sleep(0.5)
                return msg
    else:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            scrape = BeautifulSoup(response.text, "html.parser")
            inputs = scrape.find_all("input")
            file_id = inputs[1]["value"]
            file_name = re.findall("URL=(.*?) - ", response.text)[0].split("]")[1]
            parse = {"op": "download2", "id": file_id, "referer": url}
            response2 = await client.post(base_url, data=parse, headers=hs)
            dl_url = response2.headers["Location"]
            dl_url = dl_url.replace(" ", "%20")
            return f"File Name: {file_name}\n File Link: {url}\n Download Link: {dl_url}\n\n"


async def solidfiles(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            pageSource = response.text
            mainOptions = re.search(r"viewerOptions\'\,\ (.*?)\)\;", pageSource).group(
                1
            )
            return json.loads(mainOptions)["downloadUrl"]
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def sfile(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.1; SM-G532G Build/MMB29T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3239.83 Mobile Safari/537.36"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            url3 = BeautifulSoup(response.content, "html.parser")
            dl_url = url3.find("a", "w3-button w3-blue")["href"].replace(" ", "%20")
            return dl_url
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def sourceforge(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    link = re.findall(r"\bhttps?://sourceforge\.net\S+", url)[0]
    file_path = re.findall(r"files(.*)/download", link)[0]
    project = re.findall(r"projects?/(.*?)/files", link)[0]
    mirrors = (
        f"https://sourceforge.net/settings/mirror_choices?"
        f"projectname={project}&filename={file_path}"
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(mirrors)
            page = BeautifulSoup(response.content, "html.parser")
            info = page.find("ul", {"id": "mirrorList"}).findAll("li")
            for mirror in info[1:]:
                return f'https://{mirror["id"]}.dl.sourceforge.net/project/{project}/{file_path}?viasf=1'
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def sourceforge2(url):
    return f"{url}" + "?viasf=1"


async def streamlare(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    CONTENT_ID = re.compile(r"/[ve]/([^?#&/]+)")
    API_LINK = "https://sltube.org/api/video/download/get"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4136.7 Safari/537.36"
    client = requests.Session()
    content_id = CONTENT_ID.search(url).group(1)
    try:
        r = client.get(url).text
        soup = BeautifulSoup(r, "html.parser")
        csrf_token = soup.find("meta", {"name": "csrf-token"}).get("content")
        xsrf_token = client.cookies.get_dict()["XSRF-TOKEN"]
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "x-csrf-token": csrf_token,
            "x-xsrf-token": xsrf_token,
            "referer": url,
            "user-agent": user_agent,
        }
        payload = {"id": content_id}
        dl_url = client.post(API_LINK, headers=headers, data=payload).json()["result"][
            "Original"
        ]["url"]
        return dl_url
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def streamtape(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if videolink := re.findall(r"document.*((?=id\=)[^\"']+)", response.text):
                nexturl = "https://streamtape.com/get_video?" + videolink[-1]
                return nexturl
    except BaseException:
        return "Could not Generate Direct Link for your StreamTape Link :("


async def terabox(url) -> str:
    if not url_exists(url):
        return "Bot could not connect to the URL!"

    if not os.path.isfile("terabox_cookies.txt"):
        LOGGER(__name__).info("TeraBox Error: Cookies not Provided!")
        return "TeraBox Cookies not Provided!"
    dl_links = ""
    try:
        client = requests.Session()
        res = client.request("GET", url)
        key = res.url.split("?surl=")[-1]
        jar = MozillaCookieJar("terabox_cookies.txt")
        jar.load()
        client.cookies.update(jar)
        res = client.request(
            "GET",
            f"https://www.terabox.com/share/list?app_id=250528&shorturl={key}&root=1",
        )
        results = res.json()["list"]
        for result in results:
            if result["isdir"] != "0":
                dl_links += result["dlink"]
    except Exception as e:
        return f"ERROR: {e.__class__.__name__}"
    if dl_links != "":
        return dl_links
    else:
        return "Could not Generate Direct Link for your TeraBox Link :("


async def uploadbaz(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    url = url[:-1] if url[-1] == "/" else url
    token = url.split("/")[-1]
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    }
    data = {
        "op": "download2",
        "id": token,
        "rand": "",
        "referer": "",
        "method_free": "",
        "method_premium": "",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            return response.headers["Location"]
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def uploadee(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            soup = BeautifulSoup(response.content, "lxml")
            sa = soup.find("a", attrs={"id": "d_l"})
            return sa["href"]
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def uppit(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    url = url[:-1] if url[-1] == "/" else url
    token = url.split("/")[-1]
    client = requests.Session()
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    }
    data = {
        "op": "download2",
        "id": token,
        "rand": "",
        "referer": "",
        "method_free": "",
        "method_premium": "",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            soup = BeautifulSoup(response.text, "html.parser")
            download_url = soup.find(
                "span",
                {"style": "background:#f9f9f9;border:1px dotted #bbb;padding:7px;"},
            ).a.get("href")
            return download_url
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def userscloud(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    url = url[:-1] if url[-1] == "/" else url
    token = url.split("/")[-1]
    client = requests.Session()
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    }
    data = {
        "op": "download2",
        "id": token,
        "rand": "",
        "referer": "",
        "method_free": "",
        "method_premium": "",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            return response.headers["Location"]
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def uptobox(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"

    if UPTOBOX_TOKEN is None:
        LOGGER(__name__).info("UPTOBOX Error: Token not Provided!")
        return "UptoBox Token not Provided!"
    utb_tok = UPTOBOX_TOKEN

    try:
        link = re.findall(r"\bhttps?://.*uptobox\.com\S+", url)[0]
    except IndexError:
        return "No Uptobox links found"
    if utb_tok is None:
        LOGGER(__name__).error("UPTOBOX_TOKEN not provided!")
        dl_url = link
    else:
        try:
            link = re.findall(r"\bhttp?://.*uptobox\.com/dl\S+", url)[0]
            dl_url = link
        except BaseException:
            file_id = re.findall(r"\bhttps?://.*uptobox\.com/(\w+)", url)[0]
            file_link = (
                f"https://uptobox.com/api/link?token={utb_tok}&file_code={file_id}"
            )
            req = requests.get(file_link)
            result = req.json()
            if result["message"].lower() == "success":
                dl_url = result["data"]["dlLink"]
            elif result["message"].lower() == "waiting needed":
                waiting_time = result["data"]["waiting"] + 1
                waiting_token = result["data"]["waitingToken"]
                sleep(waiting_time)
                req2 = requests.get(f"{file_link}&waitingToken={waiting_token}")
                result2 = req2.json()
                dl_url = result2["data"]["dlLink"]
            elif (
                result["message"].lower()
                == "you need to wait before requesting a new download link"
            ):
                waiting_time = result["data"]["waiting"]
                cooldown = divmod(waiting_time, 60)
                mins = cooldown[0]
                secs = cooldown[1]
                return f"Uptobox is being limited. Please wait {mins} min {secs} sec."
            else:
                err = result["message"]
                LOGGER(__name__).info(f"UPTOBOX Error: {err}")
                return f"{err}"
    return dl_url


async def uservideo(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    try:
        return Bypass().bypass_uservideo(url)
    except BaseException:
        return "Could not Generate Direct Link for your UserVideo Link :("


async def wetransfer(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    try:
        if url.startswith("https://we.tl/"):
            r = requests.head(url)
            url = r.url
        recipient_id = None
        params = urllib.parse.urlparse(url).path.split("/")[2:]
        if len(params) == 2:
            transfer_id, security_hash = params
        elif len(params) == 3:
            transfer_id, recipient_id, security_hash = params
        else:
            return None
        j = {
            "intent": "entire_transfer",
            "security_hash": security_hash,
        }
        if recipient_id:
            j["recipient_id"] = recipient_id
        async with httpx.AsyncClient() as s:
            r = await s.get("https://wetransfer.com/")
            m = re.search('name="csrf-token" content="([^"]+)"', r.text)
            s.headers.update(
                {"x-csrf-token": m[1], "x-requested-with": "XMLHttpRequest"}
            )
            r = await s.post(
                f"https://wetransfer.com/api/v4/transfers/{transfer_id}/download",
                json=j,
            )
            j = r.json()
            dl_url = j["direct_link"].replace(" ", "%20")
            return dl_url
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def yandex_disk(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    api = "https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api.format(url))
            dl_url = response.json()["href"].replace(" ", "%20")
            return dl_url
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"


async def zippyshare(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    try:
        file = zippy_info(url, download=False)
        return file.download_url
    except BaseException:
        return "Some Error Occurred \nCould not generate dl-link for your URL"
