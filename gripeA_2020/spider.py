#!/usr/bin/env python

import json
import requests
from bs4 import BeautifulSoup

class scrapping(object):
    def __init__(self):
        self.search_request = {

        }

    def scrape(self):
        jobs = self.scrape_jobs()
        for job in jobs:
            print(job)

    def scrape_jobs(self, max_pages=2):

        payload = json.dumps(self.search_request)

        r = requests.get(
            url='http://empres-i.fao.org/empres-i/obdj?id=287665&lang=EN',
            data=payload,
            headers={
                'Host': 'empres-i.fao.org',
                # 'Connection': 'keep-alive',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                #'DNT': '1',
                'X-Requested-With': 'XMLHttpRequest',
                # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57',
                #'Referer': 'http://empres-i.fao.org/empres-i/2/obd?idOutbreak=287665',
                #'Accept-Encoding': 'gzip',
                #'Accept-Language': 'en'
            }
        )

        s = json.loads(r.text)
        casos = s['outbreak']['speciesAffectedList'][0]['cases']
        muertes = s['outbreak']['speciesAffectedList'][0]['deaths']

        return casos, muertes


if __name__ == '__main__':
    scraper = scrapping()
    scraper.scrape()