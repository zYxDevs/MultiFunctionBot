import asyncio
import re
import time
import urllib.parse
from base64 import b64decode

import cloudscraper
import httpx
from bs4 import BeautifulSoup
from PyBypass import bypass as pybyp

from bot.config import *
from bot.helpers.functions import api_checker, url_exists


def decrypt_url(code):
    a, b = "", ""
    for i in range(len(code)):
        if i % 2 == 0:
            a += code[i]
        else:
            b = code[i] + b
    key = list(a + b)
    i = 0
    while i < len(key):
        if key[i].isdigit():
            for j in range(i + 1, len(key)):
                if key[j].isdigit():
                    u = int(key[i]) ^ int(key[j])
                    if u < 10:
                        key[i] = str(u)
                    i = j
                    break
        i += 1
    key = "".join(key)
    decrypted = b64decode(key)[16:-16]
    return decrypted.decode("utf-8")


async def adfly(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"

    async with httpx.AsyncClient() as client:
        res = await client.get(url)
    out = {"error": False, "src_url": url}
    try:
        ysmm = re.findall("ysmm\s+=\s+['|\"](.*?)['|\"]", res.text)[0]
        url = decrypt_url(ysmm)
        await asyncio.sleep(10)
        if re.search(r"go\.php\?u\=", url):
            url = b64decode(re.sub(r"(.*?)u=", "", url)).decode()
        elif "&dest=" in url:
            url = urllib.parse.unquote(re.sub(r"(.*?)dest=", "", url))
        out["bypassed_url"] = url
        return out["bypassed_url"]
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def adrinolinks(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"

    async with httpx.AsyncClient() as client:
        dom = "https://adrinolinks.in"
        code = url.split("/")[-1]
        f_url = f"{dom}/{code}"
        hs = {
            "referer": "https://wikitraveltips.com/",
        }
        try:
            resp = await client.get(f_url, headers=hs)
            soup = BeautifulSoup(resp.text, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            h = {"x-requested-with": "XMLHttpRequest"}
            await asyncio.sleep(5)
            r = await client.post(f"{dom}/links/go", data=data, headers=h)
            des_url = r.json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def bifm(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"

    async with httpx.AsyncClient() as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
        }
        apix = f"{BIFM_URL}={url}"
        await asyncio.sleep(2)
        response = await client.get(apix, headers=headers)
    try:
        query = response.json()
    except BaseException:
        return "Invalid Link"
    if "destination" in query:
        return query["destination"]
    else:
        return query["error"]


async def droplink(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"

    async with httpx.AsyncClient() as client:
        dom = "https://droplink.co"
        h = {"referer": "https://yoshare.net"}
        try:
            res = await client.get(url, headers=h)
            soup = BeautifulSoup(res.text, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            await asyncio.sleep(4)
            headers = {"x-requested-with": "XMLHttpRequest"}
            des_url = (
                await client.post(f"{dom}/links/go", data=data, headers=headers)
            ).json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def dulink(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"

    async with httpx.AsyncClient() as client:
        dom = "https://cac.teckypress.in"
        ref = "https://teckypress.in/"
        url = url[:-1] if url[-1] == "/" else url
        code = url.split("/")[-1]
        final_url = f"{dom}/{code}"
        h = {"referer": ref}
        try:
            resp = await client.get(final_url, headers=h)
            soup = BeautifulSoup(await resp.text(), "html.parser")
            inputs = soup.find_all("input")
            data = {input.get("name"): input.get("value") for input in inputs}
            h = {"x-requested-with": "XMLHttpRequest"}
            des_url = (
                await client.post(f"{dom}/links/go", data=data, headers=h)
            ).json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def ez4short(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"

    async with httpx.AsyncClient() as client:
        dom = "https://ez4short.com"
        ref = "https://techmody.io/"
        h = {"referer": ref}
        try:
            resp = await client.get(url, headers=h)
            soup = BeautifulSoup(await resp.text(), "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            h = {"x-requested-with": "XMLHttpRequest"}
            await asyncio.sleep(8)
            des_url = (
                await client.post(f"{dom}/links/go", data=data, headers=h)
            ).json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def gplinks(url):
    url = url[:-1] if url[-1] == "/" else url
    dom = "https://gplinks.co"
    ref = "https://mynewsmedia.co/"

    async with httpx.AsyncClient() as client:
        h = {"referer": ref}
        try:
            vid = (await client.get(url)).headers["Location"].split("=")[-1]
            final_url = f"{url}/?{vid}"
            resp = await client.get(final_url, headers=h)
            soup = BeautifulSoup(resp.text, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            h = {"x-requested-with": "XMLHttpRequest"}
            await asyncio.sleep(6)
            des_url = (
                await client.post(f"{dom}/links/go", data=data, headers=h)
            ).json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def gtlinks(url):
    async with httpx.AsyncClient() as client:
        url = url[:-1] if url[-1] == "/" else url
        if "theforyou.in" in url:
            token = url.split("=")[-1]
        else:
            resp = await client.get(url)
            p_url = httpx.URL(resp.url)
            token = p_url.path.split("=")[-1]
        dom = "https://go.kinemaster.cc/"
        try:
            response = await client.get(dom + token, headers={"referer": dom + token})
            soup = BeautifulSoup(response.text, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            await asyncio.sleep(5)
            headers = {"x-requested-with": "XMLHttpRequest"}
            des_url = (
                await client.post(dom + "links/go", data=data, headers=headers)
            ).json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def gyanilinks(url):
    async with httpx.AsyncClient() as client:
        dom = "https://go.kinemaster.cc"
        try:
            re = await client.get(url)
            p_url = httpx.URL(re.url)
            code = p_url.path.split("=")[-1]
            final_url = f"{dom}/{code}"
            resp = await client.get(final_url)
            soup = BeautifulSoup(resp.text, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            h = {"x-requested-with": "XMLHttpRequest"}
            await asyncio.sleep(10)
            des_url = (
                await client.post(f"{dom}/links/go", data=data, headers=h)
            ).json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def htpmovies(url):
    async with httpx.AsyncClient() as client:
        try:
            a = (await client.get(url)).text
            b = a.split('("')[-1]
            t_url = b.split('")')[0]
            t_url = t_url.replace("&m=1", "")
            param = t_url.split("/")[-1]
            dom = "https://go.theforyou.in"
            final_url = f"{dom}/{param}"
            resp = await client.get(final_url)
            soup = BeautifulSoup(resp.text, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            h = {"x-requested-with": "XMLHttpRequest"}
            await asyncio.sleep(10)
            des_url = (
                await client.post(f"{dom}/links/go", data=data, headers=h)
            ).json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def hypershort(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            token_response = await client.get(
                "https://blog.miuiflash.com/links/createToken.js"
            )
            token_regex = re.search("itsToken\.value = \S+", token_response.text)
            token = token_regex[0].split("=")[1].removesuffix('"').removeprefix(' "')
            inputs = soup.find(id="re-form").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}[
                "getData"
            ]
            next_page_link = soup.find("form").get("action")
            resp = await client.post(
                next_page_link,
                data={"itsToken": token, "get2Data": data},
                headers={"referer": next_page_link},
            )
            soup = BeautifulSoup(resp.content, "html.parser")
            data = {input.get("name"): input.get("value") for input in inputs}
            await asyncio.sleep(3)
            tokenize_url = soup.find(name="iframe", id="anonIt").get("src")
            tokenize_url_resp = await client.get(tokenize_url)
            soup = BeautifulSoup(tokenize_url_resp.content, "html.parser")
            await asyncio.sleep(1)
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            des_url = (
                await client.post(
                    "https://blog.miuiflash.com/blog/links/go",
                    data=data,
                    cookies=tokenize_url_resp.cookies,
                    headers={
                        "x-requested-with": "XMLHttpRequest",
                        "referer": tokenize_url,
                    },
                )
            ).json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def krownlinks(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        dom = "https://go.bloggertheme.xyz"
        url = url[:-1] if url[-1] == "/" else url
        code = url.split("/")[-1]
        final_url = f"{dom}/{code}"
        try:
            resp = await client.get(final_url)
            soup = BeautifulSoup(resp.content, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            h = {"x-requested-with": "XMLHttpRequest"}
            await asyncio.sleep(10)
            des_url = (
                await client.post(f"{dom}/links/go", data=data, headers=h)
            ).json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def linkbnao(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with cloudscraper.create_scraper(allow_brotli=False) as client:
        dom = "https://vip.linkbnao.com"
        ref = "https://technoloy.xyz/"
        h = {"referer": ref}
        try:
            resp = await client.get(url, headers=h)
            soup = BeautifulSoup(resp.content, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            h = {"x-requested-with": "XMLHttpRequest"}
            await asyncio.sleep(8)
            des_url = (
                await client.post(f"{dom}/links/go", data=data, headers=h)
            ).json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def linkvertise(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with cloudscraper.create_scraper(allow_brotli=False) as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        }
        try:
            data = await client.get(
                f"https://bypass.pm/bypass2?url={url}", headers=headers
            )
            query = data.json()
            if query["success"] is True:
                return query["destination"]
            else:
                data = {
                    "url": url,
                }
                async with httpx.AsyncClient() as client:
                    r = await client.post("https://api.bypass.vip/", data=data)
                    await asyncio.sleep(1)
                    return r.json()["destination"]
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def mdiskpro(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with cloudscraper.create_scraper(allow_brotli=False) as client:
        dom = "https://mdisk.pro"
        ref = "https://m.meclipstudy.in/"
        h = {"referer": ref}
        try:
            resp = await client.get(url, headers=h)
            soup = BeautifulSoup(resp.content, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            h = {"x-requested-with": "XMLHttpRequest"}
            await asyncio.sleep(8)
            des_url = (
                await client.post(f"{dom}/links/go", data=data, headers=h)
            ).json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def multi_aio(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code == 404:
            return "File not found/The link you entered is wrong!"
        data = {"url": url}
        r = await client.post("https://api.bypass.vip/", data=data)
        await asyncio.sleep(1)
        try:
            return r.json()["destination"]
        except BaseException:
            return r.json()["response"]


async def multi_bypass(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code == 404:
            return "File not found/The link you entered is wrong!"
    async with cloudscraper.create_scraper(allow_brotli=False) as client:
        try:
            f_msg = pybyp(url)
        except Exception:
            dom = await api_checker()
            api = f"{dom}/multi"
            try:
                resp = await client.post(api, json={"url": url})
                res = resp.json()
            except BaseException:
                return "Emily API Unresponsive!"
            if res["success"] is True:
                f_msg = res["url"]
            else:
                f_msg = res["msg"]
        return f_msg


ANCHOR_URL = "https://www.google.com/recaptcha/api2/anchor?ar=1&k=6Lcr1ncUAAAAAH3cghg6cOTPGARa8adOf-y9zv2x&co=aHR0cHM6Ly9vdW8uaW86NDQz&hl=en&v=1B_yv3CBEV10KtI2HJ6eEXhJ&size=invisible&cb=4xnsug1vufyr"


async def RecaptchaV3(ANCHOR_URL):
    url_base = "https://www.google.com/recaptcha/"
    post_data = "v={}&reason=q&c={}&k={}&co={}"
    client = cloudscraper.create_scraper(allow_brotli=False)
    client.headers.update({"content-type": "application/x-www-form-urlencoded"})
    matches = re.findall("([api2|enterprise]+)\/anchor\?(.*)", ANCHOR_URL)[0]
    url_base += f"{matches[0]}/"
    params = matches[1]
    res = client.get(f"{url_base}anchor", params=params)
    token = re.findall(r'"recaptcha-token" value="(.*?)"', res.text)[0]
    params = dict(pair.split("=") for pair in params.split("&"))
    post_data = post_data.format(params["v"], token, params["k"], params["co"])
    res = client.post(f"{url_base}reload", params=f'k={params["k"]}', data=post_data)
    return re.findall(r'"rresp","(.*?)"', res.text)[0]


async def ouo(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        tempurl = url.replace("ouo.press", "ouo.io")
        p = urllib.parse.urlparse(tempurl)
        id = tempurl.split("/")[-1]
        try:
            res = await client.get(tempurl)
            next_url = f"{p.scheme}://{p.hostname}/go/{id}"
            for _ in range(2):
                if res.headers.get("Location"):
                    break
                bs4 = BeautifulSoup(res.content, "lxml")
                inputs = bs4.form.findAll("input", {"name": re.compile(r"token$")})
                data = {input.get("name"): input.get("value") for input in inputs}
                await asyncio.sleep(10)
                ans = await RecaptchaV3(ANCHOR_URL)
                data["x-token"] = ans
                h = {"content-type": "application/x-www-form-urlencoded"}
                res = await client.post(next_url, data=data, headers=h)
                next_url = f"{p.scheme}://{p.hostname}/xreallcygo/{id}"
            return res.headers.get("Location")
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def privatemoviez(url):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            test = soup.text
            param = test.split('console.log("')[-1]
            t_url = param.split('");')[0]
            t_url = t_url.replace("&m=1", "")
            param = t_url.split("/")[-1]
            dom = "https://go.kinemaster.cc"
            final_url = f"{dom}/{param}"
            resp = await client.get(final_url)
            soup = BeautifulSoup(resp.content, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            h = {"x-requested-with": "XMLHttpRequest"}
            await asyncio.sleep(10)
            des_url = await client.post(f"{dom}/links/go", data=data, headers=h)
            des_url = await client.post(f"{dom}/links/go", data=data, headers=h)
            des_url = des_url.json()["url"]
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def pkin(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        url = url[:-1] if url[-1] == "/" else url
        dom = "https://go.paisakamalo.in/"
        ref = "https://techkeshri.com/"
        token = url.split("/")[-1]
        user_agent = "Mozilla/5.0 (Linux; Android 11; 2201116PI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36"
        try:
            response = await client.get(dom + token, headers={"referer": ref})
            soup = BeautifulSoup(response.content, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            await asyncio.sleep(3)
            headers = {"x-requested-with": "XMLHttpRequest", "user-agent": user_agent}
            des_url = await client.post(dom + "links/go", data=data, headers=headers)
            des_url = des_url.json()["url"]
            return des_url
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def rewayatcafe(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        p = urllib.parse.urlparse(url)
        ref = f"{p.scheme}://{p.netloc}/"
        headers = {"referer": ref}
        try:
            res = await client.get(url, headers=headers)
            bs4 = BeautifulSoup(res.content, "html.parser")
            inputs = bs4.find_all("input")
            data = {input.get("name"): input.get("value") for input in inputs}
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "x-requested-with": "XMLHttpRequest",
            }
            p = urllib.parse.urlparse(url)
            final_url = f"{p.scheme}://{p.netloc}/links/go"
            await asyncio.sleep(10)
            des_url = await client.post(final_url, data=data, headers=headers)
            des_url = des_url.json()["url"]
            return des_url
        except Exception:
            return "Some Error Occurred \nCould not Bypass your URL"


async def rocklinks(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    ref = "https://disheye.com/"
    h = {"referer": ref}
    if "rocklinks.net" in url:
        dom = "https://rl.techysuccess.com"
    else:
        dom = "https://rocklinks.net"
    url = url[:-1] if url[-1] == "/" else url
    code = url.split("/")[-1]
    if "rocklinks.net" in url:
        final_url = f"{dom}/{code}?quelle="
    else:
        final_url = f"{dom}/{code}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(final_url, headers=h)
        soup = BeautifulSoup(resp.content, "html.parser")
        inputs = soup.find(id="go-link").find_all(name="input")
        data = {input.get("name"): input.get("value") for input in inputs}
        h = {"x-requested-with": "XMLHttpRequest"}
        await asyncio.sleep(10)
        async with httpx.AsyncClient() as client:
            des_url = await client.post(f"{dom}/links/go", data=data, headers=h)
        des_url = des_url.json()["url"]
        des_url = des_url.replace(" ", "%20")
        return des_url
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def script(url):
    try:
        await scriptb(url)
    except BaseException:
        client = requests.session()
        await scripta(f"https://{url.split('/')[-2]}/", url, client)


async def scripta(dom, url, client):
    res = client.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    soup = soup.find("form").findAll("input")
    datalist = []
    for ele in soup:
        datalist.append(ele.get("value"))
    data = {
        "_method": datalist[0],
        "_csrfToken": datalist[1],
        "ad_form_data": datalist[2],
        "_Token[fields]": datalist[3],
        "_Token[unlocked]": datalist[4],
    }
    client.headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": dom,
        "Connection": "keep-alive",
        "Referer": url,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    time.sleep(10)  # important
    response = client.post(dom + "/links/go", data=data).json()
    furl = response["url"]
    return furl


async def scriptb(url):
    global rurl
    client = requests.session()
    res = client.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    soup = soup.find("form")
    action = soup.get("action")
    soup = soup.findAll("input")
    datalist = []
    for ele in soup:
        datalist.append(ele.get("value"))
    client.headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Origin": action,
        "Connection": "keep-alive",
        "Referer": action,
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }
    data = {
        "newwpsafelink": datalist[1],
        "g-recaptcha-response": await RecaptchaV3(ANCHOR_URL),
    }
    response = client.post(action, data=data)
    soup = BeautifulSoup(response.text, "html.parser")
    soup = soup.findAll("div", class_="wpsafe-bottom text-center")
    for ele in soup:
        rurl = ele.find("a").get("onclick")[13:-12]
    res = client.get(rurl)
    furl = res.url
    return await scripta(f"https://{furl.split('/')[-2]}/", furl, client)


async def shareus(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    token = url.split("=")[-1]
    try:
        des_url = (
            f"https://us-central1-my-apps-server.cloudfunctions.net/r?shortid={token}"
        )
        async with httpx.AsyncClient() as client:
            dest_url = await client.get(des_url)
        dest_url = dest_url.text
        return dest_url
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def shorte(url):
    client = httpx.AsyncClient()
    client.headers.update({"referer": url})
    p = urllib.parse.urlparse(url)
    try:
        async with client:
            res = await client.get(url)
        sess_id = re.findall("""sessionId(?:\s+)?:(?:\s+)?['|"](.*?)['|"]""", res.text)[
            0
        ]
        final_url = f"{p.scheme}://{p.netloc}/shortest-url/end-adsession"
        params = {"adSessionId": sess_id, "callback": "_"}
        await asyncio.sleep(5)
        async with client:
            res = await client.get(final_url, params=params)
        dest_url = re.findall('"(.*?)"', res.text)[1].replace("\/", "/")
        dest_url = dest_url.replace(" ", "%20")
        return dest_url
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def short2url(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = httpx.AsyncClient()
    dom = "https://techyuth.xyz/blog"
    ref = "https://techeysub.online/"
    try:
        if ("short2url." and "/full?api=") in url:
            async with client:
                url = await client.get(url)
            url = url.text
            url = url[:-1] if url[-1] == "/" else url
            code = url.split("/")[-1].replace("?", "")
        else:
            code = url.split("/")[-1]
        final_url = f"{dom}/{code}"
        async with client:
            resp = await client.get(final_url, headers={"referer": ref})
        soup = BeautifulSoup(resp.content, "html.parser")
        inputs = soup.find_all("input")
        data = {input.get("name"): input.get("value") for input in inputs}
        h = {"x-requested-with": "XMLHttpRequest"}
        await asyncio.sleep(10)
        async with client:
            des_url = await client.post(f"{dom}/links/go", data=data, headers=h)
        des_url = des_url.json()["url"]
        des_url = des_url.replace(" ", "%20")
        return des_url
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def shortingly(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    dom = "https://go.gyanitheme.com"
    url = url[:-1] if url[-1] == "/" else url
    code = url.split("/")[-1]
    try:
        if ("shortingly." and "/full?api=") in url:
            async with httpx.AsyncClient() as client:
                res = await client.get(url)
            res = res.text
            code = res.split("=")[-1]
        final_url = f"{dom}/{code}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(final_url)
        soup = BeautifulSoup(resp.content, "html.parser")
        inputs = soup.find(id="go-link").find_all(name="input")
        data = {input.get("name"): input.get("value") for input in inputs}
        h = {"x-requested-with": "XMLHttpRequest"}
        await asyncio.sleep(10)
        async with httpx.AsyncClient() as client:
            des_url = await client.post(f"{dom}/links/go", data=data, headers=h)
        des_url = des_url.json()["url"]
        des_url = des_url.replace(" ", "%20")
        return des_url
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def shortly(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    url = url[:-1] if url[-1] == "/" else url
    token = url.split("/")[-1]
    shortly_bypass_api = "https://www.shortly.xyz/getlink.php/"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                shortly_bypass_api,
                data={"id": token},
                headers={"referer": "https://www.shortly.xyz/link"},
            )
        response = response.text
        return response
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def sirigan(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        await asyncio.sleep(3)
        try:
            res = await client.get(url)
            url = res.text.split("=", maxsplit=1)[-1]
            while True:
                try:
                    url = b64decode(url).decode("utf-8")
                except BaseException:
                    break
            return url.split("url=")[-1]
        except BaseException:
            return "Some Error Occurred \nCould not Bypass your URL"


async def try2link(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    dom = "https://try2link.net"
    ref = "https://mobi2c.com/"
    url = url[:-1] if url[-1] == "/" else url
    params = (("d", int(time.time()) + (60 * 4)),)
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, headers={"Referer": ref})
        soup = BeautifulSoup(r.text, "html.parser")
        inputs = soup.find(id="go-link").find_all(name="input")
        data = {input.get("name"): input.get("value") for input in inputs}
        await asyncio.sleep(7)
        headers = {
            "Host": "try2link.net",
            "X-Requested-With": dom,
            "Origin": dom,
            "Referer": url,
        }
        async with httpx.AsyncClient() as client:
            des_url = await client.post(f"{dom}/links/go", headers=headers, data=data)
        des_url = des_url.json()["url"]
        des_url = des_url.replace(" ", "%20")
        return des_url
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def thinfi(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    try:
        des_url = BeautifulSoup(response.content, "html.parser").p.a.get("href")
        des_url = des_url.replace(" ", "%20")
        return des_url
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def tnlink(url):
    if not url_exists(url):
        return "Bot could not connect to the URL!"
    client = httpx.AsyncClient()
    dom = "https://gadgets.usanewstoday.club"
    url = url[:-1] if url[-1] == "/" else url
    code = url.split("/")[-1]
    final_url = f"{dom}/{code}"
    ref = "https://usanewstoday.club/"
    h = {"referer": ref}
    try:
        resp = await client.get(final_url, headers=h)
        soup = BeautifulSoup(resp.content, "html.parser")
        inputs = soup.find_all(name="input")
        data = {input.get("name"): input.get("value") for input in inputs}
        h = {"x-requested-with": "XMLHttpRequest"}
        await asyncio.sleep(12)
        des_url = await client.post(f"{dom}/links/go", data=data, headers=h)
        des_url = des_url.json()["url"]
        return des_url
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def urlsopen(url):
    client = httpx.AsyncClient()
    dom = "https://blogpost.viewboonposts.com"
    url = url[:-1] if url[-1] == "/" else url
    code = url.split("/")[-1]
    final_url = f"{dom}/{code}"
    ref = "https://blog.textpage.xyz/"
    h = {"referer": ref}
    try:
        resp = await client.get(final_url, headers=h)
        soup = BeautifulSoup(resp.content, "html.parser")
        inputs = soup.find_all(name="input")
        data = {input.get("name"): input.get("value") for input in inputs}
        h = {"x-requested-with": "XMLHttpRequest"}
        await asyncio.sleep(12)
        des_url = await client.post(f"{dom}/links/go", data=data, headers=h)
        des_url = des_url.json()["url"]
        return des_url
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def vearnl(url):
    client = cloudscraper.create_scraper(allow_brotli=False)
    if ("vearnl." or "urlearn.") in url:
        dom = "https://go.urlearn.xyz"
    else:
        dom = "https://v.earnl.xyz"
    ref = "https://download.modmakers.xyz/"
    headers = {"referer": ref}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            inputs = soup.find(id="go-link").find_all(name="input")
            data = {input.get("name"): input.get("value") for input in inputs}
            headers = {"x-requested-with": "XMLHttpRequest"}
            await asyncio.sleep(8)
            response = await client.post(f"{dom}/links/go", data=data, headers=headers)
            des_url = response.json()["url"]
            des_url = des_url.replace(" ", "%20")
            return des_url
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"


async def xpshort(url):
    client = httpx.AsyncClient()
    dom = "https://push.bdnewsx.com"
    url = url[:-1] if url[-1] == "/" else url
    code = url.split("/")[-1]
    final_url = f"{dom}/{code}"
    ref = "https://techrfour.com/"
    headers = {"referer": ref}
    try:
        response = await client.get(final_url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        inputs = soup.find_all(name="input")
        data = {input.get("name"): input.get("value") for input in inputs}
        headers = {"x-requested-with": "XMLHttpRequest"}
        await asyncio.sleep(12)
        response = await client.post(f"{dom}/links/go", data=data, headers=headers)
        des_url = response.json()["url"]
        return des_url
    except BaseException:
        return "Some Error Occurred \nCould not Bypass your URL"
