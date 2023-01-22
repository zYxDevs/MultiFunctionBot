import asyncio
import json
import re
import urllib.parse
from base64 import b64decode

import cloudscraper
import requests
from bs4 import BeautifulSoup, NavigableString, Tag

from bot.helpers.functions import url_exists
from bot.logging import LOGGER
from bot.modules.bypasser import ez4short, htpmovies, privatemoviez, rocklinks, try2link
from bot.modules.pasting import telegraph_paste

drive_list = [
    "drivelinks.in",
    "driveroot.in",
    "drivesharer.in",
    "driveace.in",
    "drivehub.in",
]
next_page = False
next_page_token = ""


def index_scraper(payload, url):
    global next_page
    global next_page_token
    url = url + "/" if url[-1] != "/" else url
    client = cloudscraper.create_scraper(allow_brotli=False)
    resp = client.post(url, data=payload)
    if resp.status_code == 401:
        return "Could not Access your Entered URL!"
    try:
        resp2 = json.loads(b64decode(resp.text[::-1][24:-20]).decode("utf-8"))
    except BaseException:
        return "Something Went Wrong!"
    page_token = resp2["nextPageToken"]
    if page_token is None:
        next_page = False
    else:
        next_page = True
        next_page_token = page_token
    res = ""
    if list(resp2.get("data").keys())[0] == "error":
        pass
    else:
        file_len = len(resp2["data"]["files"])
        for i, _ in enumerate(range(file_len)):
            file_type = resp2["data"]["files"][i]["mimeType"]
            file_name = resp2["data"]["files"][i]["name"]
            if file_type == "application/vnd.google-apps.folder":
                pass
            else:
                ddl = url + urllib.parse.quote(file_name)
                res += f"• <b>{file_name}</b>:-<br><code>{ddl}</code><br><br>"
        return res


async def index_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    x = 0
    payload = {"page_token": next_page_token, "page_index": x}
    msg = f"Index Link: {url}<br><br>"
    msg += index_scraper(payload, url)
    while next_page:
        payload = {"page_token": next_page_token, "page_index": x}
        await asyncio.sleep(2)
        msg += index_scraper(payload, url)
        x += 1
    return msg


async def animeremux_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"<b>User URL :</b> <code>{url}</code><br>"
    rslt += f"<i>GDrive Links:</i><br>"
    url = url + "/" if url[-1] != "/" else url
    r = client.get(url).text
    soup = BeautifulSoup(r, "html.parser")
    for a in soup.find_all("a"):
        c = a.get("href")
        if "urlshortx." in c:
            x = c.split("url=")[-1]
            t = client.get(x).text
            soupt = BeautifulSoup(t, "html.parser")
            title = soupt.title
            rslt += f"<b>{(title.text).replace('GDToT | ', '')}</b><br><code>{x}</code><br><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def atishmkv_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"<b>User URL :</b> <code>{url}</code><br>"
    rslt += f"<i>GDrive Links:</i><br>"
    url = url + "/" if url[-1] != "/" else url
    r = client.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all(
        "a",
        {
            "class": "mb-button mb-style-traditional mb-size-small mb-corners-straight mb-text-style-heavy"
        },
    ):
        c = a.get("href")
        rslt += f"• <code>{c}</code><br>"
    for b in soup.find_all("a", {"role": "button"}):
        d = b.get("href")
        rslt += f"• <code>{d}</code><br>"
    for c in soup.find_all(
        "a",
        {
            "class": "mb-button mb-style-traditional mb-size-default mb-corners-default mb-text-style-heavy"
        },
    ):
        e = c.get("href")
        rslt += f"• <code>{e}</code><br>"
    for d in soup.find_all(
        "a",
        {
            "class": "mb-button mb-style-reversed mb-size-default mb-corners-pill mb-text-style-heavy wpel-icon-right"
        },
    ):
        f = d.get("href")
        rslt += f"• <code>{f}</code><br>"
    for e in soup.find_all(
        "a",
        {
            "class": "mb-button mb-style-reversed mb-size-default mb-corners-pill mb-text-style-heavy"
        },
    ):
        g = e.get("href")
        rslt += f"• <code>{g}</code><br>"
    for f in soup.find_all(
        "a",
        {"class": "button button-shadow wpel-icon-right"},
    ):
        h = f.get("href")
        rslt += f"• <code>{h}</code><br>"
    for g in soup.find_all(
        "a",
        {"class": "wpel-icon-right"},
    ):
        i = g.get("href")
        rslt += f"• <code>{i}</code><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def benzmovies_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"<b>User URL :</b> <code>{url}</code><br>"
    rslt += f"<i>Links:</i><br>"
    url = url + "/" if url[-1] != "/" else url
    p = client.get(url)
    soup = BeautifulSoup(p.text, "html.parser")
    links = soup.select('a[href*="filepress"]')
    for a in links:
        i = a["href"]
        rslt += f"• <code>{i}</code><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def cinevez_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"<b>User URL :</b> <code>{url}</code><br><br>"
    url = url + "/" if url[-1] != "/" else url
    p = client.get(url)
    soup = BeautifulSoup(p.text, "html.parser")
    rslt += "<b><u>Magnet Torrents :</u></b><br>"
    for a in soup.find_all(
        "div", {"class": "box-content p-3 flex justify-center items-center flex-wrap"}
    ):
        for b in a.find_all("a"):
            rslt += f"• {b['href']}<br><br>"
    rslt += "<br><b><u>Direct Links :</u></b><br>"
    for c in soup.find_all(
        "div",
        {"class": "p-2 rounded flex items-center justify-between item-link text-dark"},
    ):
        for d in c.find_all("a"):
            rslt += f"• <code>{d['href']}</code><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def cinevood_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    t_urls = []
    client = requests.Session()
    rslt = f"<b>User URL :</b> <code>{url}</code><br>"
    rslt += f"<i>Links:</i><br>"
    url = url + "/" if url[-1] != "/" else url
    p = client.get(url)
    soup = BeautifulSoup(p.text, "html.parser")
    x = soup.select('a[href^="https://filepress"]')
    for a in x:
        t_urls.append(a["href"])
    for c in t_urls:
        res = client.get(c)
        soup = BeautifulSoup(res.content, "html.parser")
        title = soup.title
        rslt += f"• <b>{title}</b><br><code>{c}</code><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def filecrypt_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    res_msg = f"<b>User URL :</b> <code>{url}</code><br><br>"
    client = requests.Session()
    h1 = {
        "authority": "filecrypt.co",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "dnt": "1",
        "origin": "https://filecrypt.co",
        "referer": url,
        "sec-ch-ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    }
    url = url + "/" if url[-1] != "/" else url
    if "filecrypt" in url and "Container":  # Folder Check
        resp = client.get(url, headers=h1)
        soup = BeautifulSoup(resp.content, "html.parser")
    else:  # File Check
        with open(url, "rb") as file:
            resp = file.read()
        soup = BeautifulSoup(resp, "html.parser")
    buttons = soup.find_all("button")
    dlclink = ""
    for ele in buttons:
        line = ele.get("onclick")
        if line is not None and "DownloadDLC" in line:
            dlclink = (
                "https://filecrypt.co/DLC/"
                + line.split("DownloadDLC('")[1].split("'")[0]
                + ".html"
            )
            break
    if dlclink == "":
        return "File not found/The link you entered is wrong!"
    resp = client.get(dlclink, headers=h1)
    if resp.text == "":
        return "Sorry! Some Error occured while parsing your Link."
    else:
        h2 = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
            "Accept": "application/json, text/javascript, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "http://dcrypt.it",
            "Connection": "keep-alive",
            "Referer": "http://dcrypt.it/",
        }
        data = {
            "content": resp.text,
        }
        response = client.post(
            "http://dcrypt.it/decrypt/paste", headers=h2, data=data
        ).json()["success"]["links"]
        for link in response:
            res_msg += f"<code>{link}</code><br>"
        tlg_url = await telegraph_paste(res_msg)
        return tlg_url


async def htpmovies_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"<b>User URL :</b> <code>{url}</code><br><br>"
    url = url + "/" if url[-1] != "/" else url
    dom = url.split("/")[-3]
    p = client.get(url)
    soup = BeautifulSoup(p.text, "html.parser")
    rslt += "<b><u>Gdrive Links :</u></b><br>"
    for a in soup.find_all("a"):
        c = a.get("href")
        if "/exit.php?url=" in c:
            temp_u = f"https://{dom}" + c
            byp = await htpmovies(temp_u)
            p = client.get(byp)
            soup = BeautifulSoup(p.content, "html.parser")
            ss = soup.select("li.list-group-item")
            li = []
            for item in ss:
                li.append(item.string)
            try:
                text = re.sub(r"www\S+ \- ", "", li[0])
            except IndexError:
                await asyncio.sleep(2)
                p = client.get(byp)
                soup = BeautifulSoup(p.content, "html.parser")
                ss = soup.select("li.list-group-item")
                li = []
                for item in ss:
                    li.append(item.string)
                text = re.sub(r"www\S+ \- ", "", li[0])
            if text is not None:
                rslt += f"• {text} <code>{byp}</code><br>"
            else:
                rslt += f"• <code>{byp}</code><br>"
    rslt += "<br><b><u>Telegram Links :</u></b><br>"
    for b in soup.find_all("a"):
        d = b.get("href")
        if "telegram.me/htpfilesbot" in d:
            rslt += f"• <code>{d}</code><br>"
    rslt += "<br><br><b><u>NOTE:</u></b><i>The GDrive Links are actually GTLinks AdLinks. Bypass them manually</i>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


def decodeKey(encoded):
    key = ""
    i = len(encoded) // 2 - 5
    while i >= 0:
        key += encoded[i]
        i = i - 2
    i = len(encoded) // 2 + 4
    while i < len(encoded):
        key += encoded[i]
        i = i + 2
    return key


async def bypassBluemediafiles(url, torrent=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Alt-Used": "bluemediafiles.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    script = str(soup.findAll("script")[3])
    encodedKey = script.split('Create_Button("')[1].split('");')[0]
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": url,
        "Alt-Used": "bluemediafiles.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    params = {"url": decodeKey(encodedKey)}
    if torrent:
        res = requests.get(
            "https://dl.pcgamestorrents.org/get-url.php", params=params, headers=headers
        )
        soup = BeautifulSoup(res.text, "html.parser")
        furl = soup.find("a", class_="button").get("href")
    else:
        res = requests.get(
            "https://bluemediafiles.com/get-url.php", params=params, headers=headers
        )
        furl = res.url
        if "mega.nz" in furl:
            furl = furl.replace("mega.nz/%23!", "mega.nz/file/").replace("!", "#")
    return furl


async def igggames_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    res_text = f"<b>User URL :</b> <code>{url}</code><br>"
    res_text += f"<i>Links/Magnets Below:</i><br>"
    url = url + "/" if url[-1] != "/" else url
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    soup = soup.find("div", class_="uk-margin-medium-top").findAll("a")
    bluelist = []
    for ele in soup:
        bluelist.append(ele.get("href"))
    bluelist = bluelist[8:-1]
    for ele in bluelist:
        if "bluemediafiles." in ele:
            temp_res = await bypassBluemediafiles(ele, False)
            res_text += f"{temp_res}<br>"
        elif "pcgamestorrents.com" in ele:
            res2 = requests.get(ele)
            soup = BeautifulSoup(res2.text, "html.parser")
            turl = (
                soup.find(
                    "p", class_="uk-card uk-card-body uk-card-default uk-card-hover"
                )
                .find("a")
                .get("href")
            )
            temp_res = await bypassBluemediafiles(turl, True)
            res_text += f"{temp_res}<br>"
        else:
            res_text += f"<code>{ele}</code><br>"
    res_text = res_text[:-1]
    tlg_url = await telegraph_paste(res_text)
    return tlg_url


async def magnet_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    result = f"<b>User URL :</b> <code>{url}</code><br>"
    result += f"<i>Magnets:</i><br>"
    magns = []
    url = url + "/" if url[-1] != "/" else url
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    x = soup.select('a[href^="magnet:?xt=urn:btih:"]')
    for a in x:
        magns.append(a["href"])
    for o in magns:
        result += f"• <code>{o}</code><br>"
    tlg_url = await telegraph_paste(result)
    return tlg_url


async def moviesboss_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"<b>User URL :</b> <code>{url}</code><br>"
    rslt += f"<i>Links:</i><br>"
    url = url + "/" if url[-1] != "/" else url
    p = client.get(url, allow_redirects=True)
    soup = BeautifulSoup(p.text, "html.parser")
    links = soup.select('a[href^="https://themoviesboss.mx/links/"]')
    for a in links:
        i = a["href"]
        r1 = client.get(i)
        soup2 = BeautifulSoup(r1.text, "html.parser")
        lnks = soup2.select('a[href^="https://links.inbbotlist.com/links/"]')
        for b in lnks:
            j = b["href"]
            r2 = client.get(j)
            soup3 = BeautifulSoup(r2.text, "html.parser")
            lks = soup3.select('a[href^="https://filepress.lol/file/"]')
            for c in lks:
                k = c["href"]
                rslt += f"• <code>{k}</code><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def moviesdrama_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"<b>User URL :</b> <code>{url}</code><br>"
    rslt += f"<i>Links:</i><br>"
    url = url + "/" if url[-1] != "/" else url
    p = client.get(url)
    soup = BeautifulSoup(p.text, "html.parser")
    for a in soup.find("div", {"class": "fix-table"}):
        for b in a.find_all("a"):
            q = b["href"]
            r = client.get(q)
            soup2 = BeautifulSoup(r.text, "html.parser")
            for c in soup2.find_all("a"):
                f_url = c["href"]
                if "moviesdrama." not in f_url:
                    rslt += f"• <code>{f_url}</code><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def moviesmod_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"<b>User URL :</b> <code>{url}</code><br>"
    url = url + "/" if url[-1] != "/" else url
    p = client.get(url)
    soup = BeautifulSoup(p.text, "html.parser")
    links = soup.select("a[rel='noopener nofollow external noreferrer']")
    for l in links:
        rslt += f"<br>{(l.text).replace('Download Links', '🏷 Download Links')} :<br>"
        scrapper = cloudscraper.create_scraper(allow_brotli=False)
        res = scrapper.get(l["href"])
        nsoup = BeautifulSoup(res.text, "html.parser")
        for ll in nsoup.select("a[href]"):
            for url in drive_list:
                if url in ll["href"]:
                    nl = (client.get(ll["href"]).text).split('"')[1]
                    rslt += f"• <code>https://{url}{nl}</code><br>"
            if "urlflix." in ll["href"]:
                resp = client.get(ll["href"])
                ssoup = BeautifulSoup(resp.text, "html.parser")
                atag = ssoup.select('div[id="text-url"] > a[href]')
                for ref in atag:
                    rslt += f"• <code>{ref['href']}</code><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def privatemoviez_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"<b>User URL :</b> <code>{url}</code><br>"
    rslt += "<b><u>Links :</u></b><br>"
    url = url + "/" if url[-1] != "/" else url
    r = client.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all(
        "a",
        {
            "class": "wp-block-button__link has-blush-bordeaux-gradient-background has-background"
        },
    ):
        try:
            d = a.get("href")
            f_url = await privatemoviez(d)
            rslt += f"• {f_url}<br>"
        except BaseException:
            continue
    for b in soup.find_all(
        "a",
        {
            "class": "wp-block-button__link has-midnight-gradient-background has-background"
        },
    ):
        try:
            e = b.get("href")
            f_url = await privatemoviez(e)
            rslt += f"• {f_url}<br>"
        except BaseException:
            continue
    for c in soup.find_all(
        "a",
        {"class": "wp-block-button__link has-background"},
    ):
        try:
            f = c.get("href")
            f_url = await privatemoviez(f)
            rslt += f"• {f_url}<br>"
        except BaseException:
            continue
    rslt += "<br><br><b><u>NOTE:</u></b><i>The GDrive Links are actually GTLinks AdLinks. Bypass them manually</i>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def sharespark_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    rslt = f"<b>User URL :</b> <code>{url}</code><br><br>"
    client = requests.Session()
    url = "?action=printpage;".join(url.split("?"))
    res = client.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    for br in soup.findAll("br"):
        next_s = br.nextSibling
        if not (next_s and isinstance(next_s, NavigableString)):
            continue
        next2_s = next_s.nextSibling
        if next2_s and isinstance(next2_s, Tag) and next2_s.name == "br":
            if str(next_s).strip():
                List = next_s.split()
                if re.match(r"^(480p|720p|1080p)(.+)? Links:\Z", next_s):
                    rslt += (
                        f'<b>{next_s.replace("Links:", "GDToT Links :")}</b><br><br>'
                    )
                for s in List:
                    ns = re.sub(r"\(|\)", "", s)
                    if re.match(r"https?://.+\.gdtot\.\S+", ns):
                        r = client.get(ns)
                        soup = BeautifulSoup(r.content, "html.parser")
                        title = soup.select('meta[property^="og:description"]')
                        rslt += f"<code>{(title[0]['content']).replace('Download ' , '')}</code><br>{ns}<br><br>"
                    elif re.match(r"https?://pastetot\.\S+", ns):
                        nxt = re.sub(r"\(|\)|(https?://pastetot\.\S+)", "", next_s)
                        rslt += f"<br><code>{nxt}</code><br>{ns}<br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def skymovieshd_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"<b>User URL :</b> <code>{url}</code><br>"
    url = url + "/" if url[-1] != "/" else url
    p = client.get(url)
    soup = BeautifulSoup(p.text, "html.parser")
    a = soup.select('a[href^="https://howblogs.xyz"]')
    t = soup.select('div[class^="Robiul"]')
    rslt += f"<i>{t[-1].text.replace('Download ', '')}</i><br><br>"
    rslt += f"<b>{a[0].text} :</b></br>"
    nres = client.get(a[0]["href"], allow_redirects=False)
    nsoup = BeautifulSoup(nres.text, "html.parser")
    atag = nsoup.select('div[class="cotent-box"] > a[href]')
    for no, link in enumerate(atag, start=1):
        rslt += f"• {no}. <code>{link['href']}</code><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def olamovies_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    url = url + "/" if url[-1] != "/" else url
    res_mesg = f"<b>User URL :</b> <code>{url}</code><br>"
    res_mesg += f"<i>Direct Download Links:</i><br>"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": url,
        "Alt-Used": "olamovies.ink",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }

    client = cloudscraper.create_scraper()
    res = client.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    soup = soup.findAll("div", class_="wp-block-button")

    outlist = []
    for ele in soup:
        outlist.append(ele.find("a").get("href"))

    slist = []
    for ele in outlist:
        try:
            key = (
                ele.split("?key=")[1]
                .split("&id=")[0]
                .replace("%2B", "+")
                .replace("%3D", "=")
                .replace("%2F", "/")
            )
            id = ele.split("&id=")[1]
        except BaseException:
            continue
        count = 3
        params = {"key": key, "id": id}
        soup = "None"
        LOGGER(__name__).info(f"Trying OlaMovies Scraping with Link : {url}!")
        url = "https://olamovies.wtf/download/&key=" + key + "&id=" + id
        while ("rocklinks." and "try2link." and "ez4short.com") not in soup:
            res = client.get(
                "https://olamovies.ink/download/", params=params, headers=headers
            )
            rand = res.text
            rose = rand.split('url = "')[-1]
            soup = rose.split('";')[0]
            if soup != "":
                if ("try2link." or "rocklinks." or "ez4short.") in soup:
                    LOGGER(__name__).info(f"Added {soup} in OlaMovies Scraping")
                    slist.append(soup)
                else:
                    LOGGER(__name__).info(f"Not Added {soup} in OlaMovies Scraping")
            else:
                if count == 0:
                    break
                else:
                    count -= 1
            await asyncio.sleep(10)

    final = []
    for ele in slist:
        if "rocklinks." in ele:
            temp_res = await rocklinks(ele)
            final.append(temp_res)
        elif "try2link." in ele:
            temp_res = await try2link(ele)
            final.append(temp_res)
        elif "ez4short.com" in ele:
            temp_res = await ez4short(ele)
            final.append(temp_res)
        else:
            final.append(ele)
    for ee in final:
        res_mesg += f"<code>{ee}</code><br>"
    tlg_url = await telegraph_paste(res_mesg)
    return tlg_url


async def try2link_scrape(url):
    client = requests.Session()
    h = {
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    }
    res = client.get(url, cookies={}, headers=h)
    url = "https://try2link.com/" + re.findall("try2link\.com\/(.*?) ", res.text)[0]
    res2 = await try2link(url)
    return res2


async def psa_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    rs_msg = f"<b>User URL :</b> <code>{url}</code><br><br>"
    client = requests.Session()
    url = url + "/" if url[-1] != "/" else url
    r = client.get(url)
    soup = BeautifulSoup(r.text, "html.parser").find_all(
        class_="dropshadowboxes-drop-shadow dropshadowboxes-rounded-corners dropshadowboxes-inside-and-outside-shadow dropshadowboxes-lifted-both dropshadowboxes-effect-default"
    )
    for link in soup:
        try:
            exit_gate = link.a.get("href")
            res = await try2link_scrape(exit_gate)
            rs_msg += f"<code>{res}</code><br>"
        except BaseException:
            pass
    tlg_url = await telegraph_paste(rs_msg)
    return tlg_url


async def taemovies_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"User URL : {url}<br><br>"
    rslt += "Gdrive Links :<br><br>"
    url = url + "/" if url[-1] != "/" else url
    res = client.get(url, allow_redirects=True)
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select('a[href*="shortingly"]')
    for a in links:
        c = a["href"]
        rslt += f"• {c}<br>"
    rslt += "<br><br><b><u>NOTE:</u></b><i>The GDrive Links are actually Shortingly AdLinks. Bypass them manually</i>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def tamiltvtoons_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    ad_urls = f"<b>User URL :</b> <code>{url}</code><br>"
    ad_urls += f"<i>AdLinks:</i><br>"
    url = url + "/" if url[-1] != "/" else url
    r = client.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select('a[href*="short2url"]')
    for a in links:
        down = client.get(a["href"], stream=True, allow_redirects=False)
        link = down.headers["location"]
        ad_urls += f"• <code>{link}</code><br><br>"
    tlg_url = await telegraph_paste(ad_urls)
    return tlg_url


async def teleguflix_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    rslt = f"User URL : {url}<br><br>"
    rslt += "Links :<br><br>"
    url = url + "/" if url[-1] != "/" else url
    res = client.get(url, allow_redirects=True)
    soup = BeautifulSoup(res.content, "html.parser")
    links = soup.select('a[href*="gdtot"]')
    for no, link in enumerate(links, start=1):
        gdlk = link["href"]
        t = client.get(gdlk)
        soupt = BeautifulSoup(t.text, "html.parser")
        title = soupt.select('meta[property^="og:description"]')
        rslt += f"{no}. <code>{(title[0]['content']).replace('Download ', '')}</code><br>{gdlk}<br><br>"
    tlg_url = await telegraph_paste(rslt)
    return tlg_url


async def toonworld4all_scrap(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = requests.Session()
    ad_urls = f"<b>User URL :</b> <code>{url}</code><br>"
    ad_urls += f"<i>AdLinks:</i><br>"
    url = url + "/" if url[-1] != "/" else url
    r = client.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a"):
        b = a["href"]
        if "redirect/main.php?" in b:
            down = client.get(a["href"], stream=True, allow_redirects=False)
            link = down.headers["location"]
            ad_urls += f"• <code>{link}</code><br><br>"
    tlg_url = await telegraph_paste(ad_urls)
    return tlg_url
