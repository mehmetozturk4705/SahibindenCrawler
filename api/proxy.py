import requests
from lxml import html
import random
import os
from datetime import datetime
from threading import Thread, Lock

class Proxy(object):
    def __init__(self, proxy_link = "https://free-proxy-list.net", suspend_timeout=60*60):
        self.__link = proxy_link
        self.__proxy_list_lock = Lock()
        self.__proxy_list = []
        self.__proxies = {}
        self.__suspend_timeout = suspend_timeout
    def fetch_proxies(self):
        self.__proxy_list = []
        response = requests.get(self.__link)
        assert response.status_code == 200
        DOM = html.fromstring(response.content)
        parsed = DOM.xpath("//table[contains(@id, 'proxylisttable')]//tbody//tr")
        for element in parsed:
            row = element.xpath("td")
            cur_ip = row[0].text
            cur_port = row[1].text
            cur_https = row[6].text
            if cur_https == "yes":
                self.__proxy_list.append(f"{cur_ip}:{cur_port}")
                self.__proxies[f"{cur_ip}:{cur_port}"] = {"suspended": False, "last_suspended": datetime.now()}

    def load_from_file(self, proxy_filepath:str):
        self.__proxies = {}
        self.__proxy_list = []
        with open(proxy_filepath, "r") as f:
            for line in f.readlines():
                current_proxy = line.strip();
                self.__proxies[current_proxy] = {"suspended": False,  "last_suspended": datetime.now()}
                self.__proxy_list.append(current_proxy)

    def proxy_generator(self):
        while True:
            for proxy in self.__proxy_list:
                with self.__proxy_list_lock:
                    current_last_suspended = self.__proxies[proxy]["last_suspended"]
                    current_suspended = self.__proxies[proxy]["suspended"]
                if (datetime.now() - current_last_suspended).total_seconds() > self.__suspend_timeout:
                    with self.__proxy_list_lock:
                        self.__proxies[proxy]["suspended"] = False
                        current_suspended = False
                if not current_suspended:
                    yield proxy
            random.shuffle(self.__proxy_list)

    def suspend_proxy(self, proxy):
        proxy = proxy.strip()
        with self.__proxy_list_lock:
            if proxy not in self.__proxy_list:
                raise Exception("Proxy is not in list.")
        with self.__proxy_list_lock:
            self.__proxies[proxy]["suspended"] = True
            self.__proxies[proxy]["last_suspended"] = datetime.now()



