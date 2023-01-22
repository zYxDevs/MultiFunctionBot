import os
import re
from time import sleep
from urllib.parse import urlparse

import chromedriver_autoinstaller
import cloudscraper
import lxml
from lxml import etree
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from bot.config import *


async def gdtot(url):
    cget = cloudscraper.create_scraper().request
    try:
        res = cget("GET", f'https://gdbot.xyz/file/{url.split("/")[-1]}')
        token_url = lxml.etree.HTML(res.content).xpath(
            "//a[contains(@class,'inline-flex items-center justify-center')]/@href"
        )[0]
        token_page = cget("GET", token_url)
    except Exception as e:
        LOGGER(__name__).error(f"ERROR: {e.__class__.__name__} with {token_url}")
        return f"ERROR: {e.__class__.__name__}"
    path = re.findall('\("(.*?)"\)', token_page.text)[0]
    raw = urlparse(token_url)
    try:
        final_url = f"{raw.scheme}://{raw.netloc}{path}"
        res = cget("GET", final_url)
    except Exception as e:
        LOGGER(__name__).error(f"ERROR: {e.__class__.__name__} with {final_url}")
        return f"ERROR: {e.__class__.__name__}"
    try:
        key = re.findall('"key",\s+"(.*?)"', res.text)[0]
    except Exception as e:
        LOGGER(__name__).error(f"ERROR: {e.__class__.__name__}")
        return f"ERROR: {e.__class__.__name__}"
    ddl_btn = lxml.etree.HTML(res.content).xpath("//button[@id='drc']")
    if not ddl_btn:
        LOGGER(__name__).error("ERROR: This link don't have direct download button")
        return "ERROR: This link don't have direct download button!"
    headers = {
        "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryi3pOrWU7hGYfwwL4",
        "x-token": raw.netloc,
    }
    data = (
        '------WebKitFormBoundaryi3pOrWU7hGYfwwL4\r\nContent-Disposition: form-data; name="action"\r\n\r\ndirect\r\n'
        f'------WebKitFormBoundaryi3pOrWU7hGYfwwL4\r\nContent-Disposition: form-data; name="key"\r\n\r\n{key}\r\n'
        '------WebKitFormBoundaryi3pOrWU7hGYfwwL4\r\nContent-Disposition: form-data; name="action_token"\r\n\r\n\r\n'
        "------WebKitFormBoundaryi3pOrWU7hGYfwwL4--\r\n"
    )
    try:
        response = cget(
            "POST", final_url, cookies=res.cookies, headers=headers, data=data
        ).json()
        res = cget("GET", response["url"])
        return lxml.etree.HTML(res.content).xpath("//a[contains(@class,'btn')]/@href")[
            0
        ]
    except Exception as e:
        LOGGER(__name__).error(f"ERROR: {e.__class__.__name__}")
        return f"ERROR: {e.__class__.__name__}"


async def unified(url: str) -> str:
    try:
        cget = cloudscraper.create_scraper().request
        raw = urlparse(url)
        res = cget("GET", url)
        key = re.findall('"key",\s+"(.*?)"', res.text)[0]
        ddl_btn = lxml.etree.HTML(res.content).xpath("//button[@id='drc']")
    except Exception as e:
        LOGGER(__name__).error(f"ERROR: {e.__class__.__name__}")
        return f"ERROR: {e.__class__.__name__}"
    if not ddl_btn:
        LOGGER(__name__).error("ERROR: This link don't have direct download button")
        return f"ERROR: This link don't have direct download button"
    headers = {
        "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryi3pOrWU7hGYfwwL4",
        "x-token": raw.netloc,
    }
    data = (
        '------WebKitFormBoundaryi3pOrWU7hGYfwwL4\r\nContent-Disposition: form-data; name="action"\r\n\r\ndirect\r\n'
        f'------WebKitFormBoundaryi3pOrWU7hGYfwwL4\r\nContent-Disposition: form-data; name="key"\r\n\r\n{key}\r\n'
        '------WebKitFormBoundaryi3pOrWU7hGYfwwL4\r\nContent-Disposition: form-data; name="action_token"\r\n\r\n\r\n'
        "------WebKitFormBoundaryi3pOrWU7hGYfwwL4--\r\n"
    )
    try:
        res = cget("POST", url, cookies=res.cookies, headers=headers, data=data).json()
        return res["url"]
    except Exception as e:
        LOGGER(__name__).error(f"ERROR: {e.__class__.__name__}")
        return f"ERROR: {e.__class__.__name__}"


async def udrive(url: str) -> str:
    client = requests.Session()
    if "hubdrive." in url:
        url = url.replace(".me", ".pw")
        if HUBDRIVE_CRYPT is None:
            return "HubDrive Crypt not provided!"
        client.cookies.update({"crypt": HUBDRIVE_CRYPT})
    if "katdrive." in url:
        if KATDRIVE_CRYPT is None:
            return "KatDrive Crypt not provided!"
        client.cookies.update({"crypt": KATDRIVE_CRYPT})
    if "kolop." in url:
        if KOLOP_CRYPT is None:
            return "Kolop Crypt not provided!"
        client.cookies.update({"crypt": KOLOP_CRYPT})
    if "drivefire." in url:
        if DRIVEFIRE_CRYPT is None:
            return "DriveFire Crypt not provided!"
        client.cookies.update({"crypt": DRIVEFIRE_CRYPT})
    if "drivebuzz." in url:
        if DRIVEBUZZ_CRYPT is None:
            return "DriveBuzz Crypt not provided!"
        client.cookies.update({"crypt": DRIVEBUZZ_CRYPT})
    if "drivehub." in url:
        if DRIVEHUB_CRYPT is None:
            return "DriveHub Crypt not provided!"
        client.cookies.update({"crypt": DRIVEHUB_CRYPT})
    if "gadrive." in url:
        if GADRIVE_CRYPT is None:
            return "GaDrive Crypt not provided!"
        client.cookies.update({"crypt": GADRIVE_CRYPT})
    if "jiodrive." in url:
        if JIODRIVE_CRYPT is None:
            return "JioDrive Crypt not provided!"
        client.cookies.update({"crypt": JIODRIVE_CRYPT})
    res = client.get(url)
    info_parsed = await parse_info(res, url)
    info_parsed["error"] = False
    up = urlparse(url)
    req_url = f"{up.scheme}://{up.netloc}/ajax.php?ajax=download"
    file_id = url.split("/")[-1]
    data = {"id": file_id}
    headers = {"x-requested-with": "XMLHttpRequest"}
    try:
        res = client.post(req_url, headers=headers, data=data).json()["file"]
    except BaseException:
        return "File Not Found or User rate exceeded !!"
    if "drivefire." in url:
        gd_id = res.rsplit("/", 1)[-1]
        flink = f"https://drive.google.com/file/d/{gd_id}"
        return flink
    elif "drivehub." in url:
        gd_id = res.rsplit("=", 1)[-1]
        flink = f"https://drive.google.com/open?id={gd_id}"
        return flink
    elif "drivebuzz." in url:
        gd_id = res.rsplit("=", 1)[-1]
        flink = f"https://drive.google.com/open?id={gd_id}"
        return flink
    else:
        try:
            gd_id = re.findall("gd=(.*)", res, re.DOTALL)[0]
        except BaseException:
            return "Unknown Error Occurred!"
        flink = f"https://drive.google.com/open?id={gd_id}"
        return flink


async def parse_info(res, url):
    info_parsed = {}
    if "drivebuzz." in url:
        info_chunks = re.findall('<td\salign="right">(.*?)<\/td>', res.text)
    elif "sharer.pw" in url:
        f = re.findall(">(.*?)<\/td>", res.text)
        info_parsed = {}
        for i in range(0, len(f), 3):
            info_parsed[f[i].lower().replace(" ", "_")] = f[i + 2]
        return info_parsed
    else:
        info_chunks = re.findall(">(.*?)<\/td>", res.text)
    for i in range(0, len(info_chunks), 2):
        info_parsed[info_chunks[i]] = info_chunks[i + 1]
    return info_parsed


async def sharerpw(url: str, forced_login=False) -> str:
    if (Sharerpw_XSRF or Sharerpw_laravel) is None:
        return "Sharerpw Cookies not Found!"
    try:
        scraper = cloudscraper.create_scraper(delay=10, browser="chrome")
        scraper.cookies.update(
            {
                "XSRF-TOKEN": Sharerpw_XSRF,
                "laravel_session": Sharerpw_laravel,
            }
        )
        res = scraper.get(url)
        token = re.findall("_token\s=\s'(.*?)'", res.text, re.DOTALL)[0]
        ddl_btn = etree.HTML(res.content).xpath("//button[@id='btndirect']")
        info_parsed = await parse_info(res, url)
        info_parsed["error"] = True
        info_parsed["src_url"] = url
        info_parsed["link_type"] = "login"
        info_parsed["forced_login"] = forced_login
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
        }
        data = {"_token": token}
        if len(ddl_btn):
            info_parsed["link_type"] = "direct"
        if not forced_login:
            data["nl"] = 1
        try:
            res = scraper.post(url + "/dl", headers=headers, data=data).json()
        except BaseException:
            return f"{info_parsed}"
        if "url" in res and res["url"]:
            info_parsed["error"] = False
            info_parsed["gdrive_link"] = res["url"]
        if len(ddl_btn) and not forced_login and "url" not in info_parsed:
            return await sharerpw(url, forced_login=True)
        return info_parsed["gdrive_link"]
    except Exception as err:
        return f"Encountered Error while parsing Link : {err}"


async def drivehubs(url: str) -> str:
    chromedriver_autoinstaller.install()

    os.chmod("/usr/src/app/chromedriver", 755)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    wd = webdriver.Chrome("/usr/src/app/chromedriver", chrome_options=chrome_options)
    wd.get(url)
    wd.find_element(By.XPATH, '//button[@id="fast"]').click()
    sleep(10)
    wd.switch_to.window(wd.window_handles[-1])
    flink = wd.current_url
    wd.close()
    if "drive.google.com" in flink:
        return flink
    else:
        return f"ERROR! Maybe Direct Download is not working for this file !\n Retrived URL : {flink}"


def filepress(url):
    cget = cloudscraper.create_scraper().request
    try:
        raw = urlparse(url)
        json_data = {
            "id": url.split("/")[-1],
            "method": "publicDownlaod",
        }
        api = f"{raw.scheme}://api.{raw.netloc}/api/file/downlaod/"
        res = cget(
            "POST",
            api,
            headers={"Referer": f"{raw.scheme}://{raw.netloc}"},
            json=json_data,
        ).json()
        if "data" not in res:
            LOGGER(__name__).error(f'ERROR: {res["statusText"]}')
            return f'ERROR: {res["statusText"]}'
        return f'https://drive.google.com/uc?id={res["data"]}&export=download'
    except Exception as e:
        LOGGER(__name__).error(f"ERROR: {e.__class__.__name__}")
        return f"ERROR: {e.__class__.__name__}"


async def shareDrive(url, directLogin=True):
    if SHAREDRIVE_PHPCKS is None:
        return "ShareDrive Cookie not Found!"
    try:
        successMsgs = ["success", "Success", "SUCCESS"]
        scrapper = requests.Session()
        cook = scrapper.get(url)
        cookies = cook.cookies.get_dict()
        PHPSESSID = cookies["PHPSESSID"]
        headers = {
            "authority": urlparse(url).netloc,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": f"https://{urlparse(url).netloc}/",
            "referer": url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35",
            "X-Requested-With": "XMLHttpRequest",
        }
        if directLogin:
            cookies = {"PHPSESSID": PHPSESSID}
            data = {"id": url.rsplit("/", 1)[1], "key": "direct"}
        else:
            cookies = {"PHPSESSID": PHPSESSID, "PHPCKS": SHAREDRIVE_PHPCKS}
            data = {"id": url.rsplit("/", 1)[1], "key": "original"}
        resp = scrapper.post(
            f"https://{urlparse(url).netloc}/post",
            headers=headers,
            data=data,
            cookies=cookies,
        )
        toJson = resp.json()
        if directLogin:
            if toJson["message"] in successMsgs:
                driveUrl = toJson["redirect"]
                return driveUrl
            else:
                await shareDrive(url, directLogin=False)
        else:
            driveUrl = toJson["redirect"]
            return driveUrl
    except Exception as err:
        return f"Encountered Error while parsing Link : {err}"


async def pahe(url: str) -> str:
    chromedriver_autoinstaller.install()

    AGREE_BUTTON = "//*[contains(text(), 'AGREE')]"
    LINK_TYPE = ["//*[contains(text(), 'GD')]"]
    GENERATE = "#generater > img"
    SHOW_LINK = "showlink"
    CONTINUE = "Continue"

    os.chmod("/usr/src/app/chromedriver", 755)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    wd = webdriver.Chrome("/usr/src/app/chromedriver", chrome_options=chrome_options)
    wd.get(url)
    texts = [
        y for x in [wd.find_elements("xpath", type) for type in LINK_TYPE] for y in x
    ]
    texts[1].click()
    if "intercelestial." not in wd.current_url:
        wd.close()
        wd.switch_to(wd.find_all(wd.switch_to.Window())[0])
        LOGGER(__name__).info("Chrome Pahe: Website Switched!")
    try:
        WebDriverWait(wd, 10).until(
            ec.element_to_be_clickable((By.XPATH, AGREE_BUTTON))
        ).click()
    except TimeoutException:
        LOGGER(__name__).info("Chrome Pahe: Browser Verification Error!")
        return "Chrome Pahe: Browser Verification Error!"
    wd.execute_script("document.getElementById('landing').submit();")
    WebDriverWait(wd, 30).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, GENERATE))
    ).click()
    WebDriverWait(wd, 45).until(ec.element_to_be_clickable((By.ID, SHOW_LINK))).click()
    window_after = wd.window_handles[1]
    wd.switch_to.window(window_after)
    wd.execute_script("window.scrollTo(0,535.3499755859375)")
    WebDriverWait(wd, 30).until(ec.element_to_be_clickable((By.LINK_TEXT, CONTINUE)))
    last = wd.find_element("link text", CONTINUE)
    sleep(5)
    wd.execute_script("arguments[0].click();", last)
    flink = wd.current_url
    wd.close()
    gd_url = await gdtot(flink)
    return gd_url
