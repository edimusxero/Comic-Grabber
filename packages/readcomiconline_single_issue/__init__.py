import binascii
import requests
from bs4 import BeautifulSoup
import re
import packages.shared_variables as sv


def populate_images(issue_url):
    response = requests.get(issue_url, headers=sv.headers)

    if 'Are you human?' in response:
        print(f'Captcha gotcha : Please visit : {issue_url} to clear this up')

    soup = BeautifulSoup(response.content, 'html.parser')

    script_tags = soup.find_all('script', type='text/javascript')

    pattern = re.compile(r"lstImages\.push\('(.+?)'\);")

    values = []

    for script_tag in script_tags:
        if script_tag.string:
            matches = re.findall(pattern, script_tag.string)
            if matches:
                values.extend(matches)

    return values


def beau(encoded_url):
    encoded_url = encoded_url.replace("_x236", "d")
    encoded_url = encoded_url.replace("_x945", "g")

    if encoded_url.startswith("https"):
        return encoded_url

    encoded_url, sep, rest = encoded_url.partition("?")
    containsS0 = "=s0" in encoded_url
    encoded_url = encoded_url[:-3 if containsS0 else -6]
    encoded_url = encoded_url[4:22] + encoded_url[25:]
    encoded_url = encoded_url[0:-6] + encoded_url[-2:]
    encoded_url = binascii.a2b_base64(encoded_url).decode()
    encoded_url = encoded_url[0:13] + encoded_url[17:]
    encoded_url = encoded_url[0:-2] + ("=s0" if containsS0 else "=s1600")
    return "https://2.bp.blogspot.com/" + encoded_url + sep + rest
