import requests
from lxml import html
import hashlib
import os
from .proxy import Proxy
import time

class SahibindenCrawler(object):
    def __init__(self, headers, load_from_file=True):
        self.__headers = headers
        self.__proxy = Proxy()

        if load_from_file:
            self.__proxy.load_from_file("proxies.txt")
        else:
            self.__proxy.fetch_proxies()

        self.__proxy_gen = self.__proxy.proxy_generator()

    def __normalizeLink(self, link):
        if link.startswith("/"):
            link = "https://www.sahibinden.com" + link
        return link

    def __parseFN(self, link:str):
        return link[(link.rfind("/")) + 1:]

    def parseLinksFromPage(self, link, result_set=[]):
        print(f"Extracting link {link}")
        cur_proxy = next(self.__proxy_gen)
        try:
            response = requests.get(link.strip(), headers=self.__headers, proxies={"http": cur_proxy, "https": cur_proxy})
            try:
                assert response.status_code == 200
                DOM = html.fromstring(response.content)
                elements = DOM.xpath("//tr[string-length(@data-id)>0]/td[1]//a")
                for element in elements:
                    result_set.append(self.__normalizeLink(element.get("href")))

                next_list = list(filter(lambda str: str["label"].strip() == "Sonraki", filter(lambda str: str["label"] is not None, map(lambda x: {"label": x.text, "url": x.get("href")}, DOM.xpath("//a[@class='prevNextBut']")))))
                if len(next_list)>0:
                    self.parseLinksFromPage(self.__normalizeLink(next_list[0]["url"]), result_set=result_set)
            except:
                print(f"Error in {link} Status code: {response.status_code}")
                if response.status_code == 429:
                    self.__proxy.suspend_proxy(cur_proxy)
                    self.parseLinksFromPage(link, result_set=result_set)
        except:
            print(f"There is a proxy error: {cur_proxy}")
            self.__proxy.suspend_proxy(cur_proxy)
            self.parseLinksFromPage(link, result_set=result_set)


        return result_set

    def parseAdvertisementPage(self, page):
        print(f"Product link {page}")
        cur_proxy = next(self.__proxy_gen)
        try:
            response = requests.get(page.strip(), headers=self.__headers, proxies={"http": cur_proxy, "https": cur_proxy} )
            try:
                assert response.status_code == 200
                DOM = html.fromstring(response.content)
                elements = DOM.xpath("//div[contains(@class, 'classifiedDetailMainPhoto')]/label/img")

                folder = f"dataset/{hashlib.md5(page.strip().encode()).hexdigest()}"
                if not os.path.isdir(folder):
                    os.mkdir(folder)

                for element in elements:
                    src = element.get("data-src")
                    if src is not None:
                        self.__findImgsAndSave(src, folder)
                        time.sleep(0.07)

            except:
                print(f"Ads page {page} Status code {response.status_code}")
                if response.status_code == 429:
                    self.__proxy.suspend_proxy(cur_proxy)
                    self.parseAdvertisementPage(page)
        except:
            print(f"There is a proxy error: {cur_proxy}")
            self.__proxy.suspend_proxy(cur_proxy)
            self.parseAdvertisementPage(page)

    def __findImgsAndSave(self, src, folder):
        cur_proxy = next(self.__proxy_gen)
        try:
            response = requests.get(src, headers=self.__headers, proxies={"http": cur_proxy, "https": cur_proxy})
            try:
                assert response.status_code == 200
                with open(os.path.join(folder, self.__parseFN(src)), "wb") as f:
                    f.write(response.content)
            except:
                print(f"Error in {src}")
                if response.status_code == 429:
                    self.__proxy.suspend_proxy(cur_proxy)
                    self.__findImgsAndSave(src, folder)
        except:
            print(f"There is a proxy error: {cur_proxy}")
            self.__proxy.suspend_proxy(cur_proxy)
            self.__findImgsAndSave(src, folder)