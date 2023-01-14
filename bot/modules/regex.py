import re

import requests
from bs4 import BeautifulSoup

URL_REGEX = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+"


def is_a_url(url: str):
    url = re.match(
        r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])",
        url,
    )
    return bool(url)


def is_bhadoo_index(url: str):
    client = requests.Session()
    url = url + "/" if url[-1] != "/" else url
    res = client.get(url, allow_redirects=True)
    soup = BeautifulSoup(res.content, "html.parser")
    x = soup.select('link[href^="https://cdn.jsdelivr.net/npm/@googledrive/index"]')
    if x:
        return bool(url)


def is_gdtot_link(url: str):
    url = re.match(r"https?://.+\.gdtot\.\S+", url)
    return bool(url)


def is_unified_link(url: str):
    url = re.match(
        r"https?://(anidrive|driveroot|driveflix|indidrive|drivehub|appdrive|driveapp|driveace|gdflix|drivelinks|drivebit|drivesharer|drivepro)\.\S+",
        url,
    )
    return bool(url)


def is_udrive_link(url: str):
    url = re.match(
        r"https?://(hubdrive|katdrive|kolop|drivefire|drivebuzz|gadrive|jiodrive)\.\S+",
        url,
    )
    return bool(url)


def is_sharedrive_link(url: str):
    url = re.match(r"https?://(sharedrive)\.pics/\S+", url)
    return bool(url)


def is_sharer_link(url: str):
    url = re.match(r"https?://(sharer)\.pw/\S+", url)
    return bool(url)


def is_drivehubs_link(url: str):
    return "drivehubs." in url


def is_artstation_link(url: str):
    url = re.match(r"artstation\.com/(?:artwork|projects)/([0-9a-zA-Z]+)", url)
    return bool(url)


def is_fichier_link(url: str):
    url = re.match(
        r"https?://(pjointe|dl4free|tenvoi|piecejointe|mesfichiers|desfichiers|megadl|dfichiers|alterupload|cjoint|1fichier|\.com/\?)\S+",
        url,
    )
    return bool(url)


def is_filepress_link(url: str):
    url = re.match(r"https?://(filepress|filebee)\.\S+", url)
    return bool(url)


def is_sendcm_folder_link(url: str):
    return (
        "https://send.cm/s/"
        or "https://send.cm/?sort"
        or "https://send.cm/?sort_field"
        or "https://send.cm/?sort_order"
    ) in url
