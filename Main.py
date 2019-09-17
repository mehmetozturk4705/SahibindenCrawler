import sys
import requests
from datetime import datetime
from api import SahibindenCrawler
import time

HOST = "www.sahibinden.com"
HEADER_STRING = f"""Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate, br
Accept-Language: tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7
Cache-Control: max-age=0
Connection: keep-alive
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"""

def parseHeaders(header_string:str):
    return {i[0]: i[1] for i in map(lambda x: x.split(": ", maxsplit=2), header_string.splitlines(False))}

if __name__ == "__main__":
    headers = parseHeaders(HEADER_STRING)
    api = SahibindenCrawler(headers, )
    crawler_link = input("Input link: ")
    for link in api.parseLinksFromPage(crawler_link):
        api.parseAdvertisementPage(link)
        time.sleep(0.05)


