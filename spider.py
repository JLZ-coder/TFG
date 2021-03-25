#!/usr/bin/env python

import json
import requests
from bs4 import BeautifulSoup

class AppleJobsScraper(object):
    def __init__(self):
        self.search_request = {

        }

    def scrape(self):
        jobs = self.scrape_jobs()
        for job in jobs:
            print(job)

    def scrape_jobs(self, max_pages=2):
        jobs = []
        pageno = 1
        self.search_request['pageNumber'] = pageno

        while pageno < max_pages:
            payload = json.dumps(self.search_request)

            r = requests.get(
                url='http://empres-i.fao.org/empres-i/obdj?id=287665&lang=EN',
                data=payload,
                headers={
                    # 'Host': 'empres-i.fao.org',
                    # 'Connection': 'keep-alive',
                    # 'Pragma': 'no-cache',
                    # 'Cache-Control': 'no-cache',
                    'Accept': 'application/json',
                    # 'DNT': '1',
                    'X-Requested-With': 'XMLHttpRequest'
                    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57',
                    # 'Referer': 'http://empres-i.fao.org/empres-i/2/obd?idOutbreak=287665',
                    #'Accept-Encoding': ['gzip', 'deflate'],
                    #'Accept-Language': ['es','es-ES;q=0.9','en;q=0.8','en-GB;q=0.7','en-US;q=0.6']
                }
            )

            s = BeautifulSoup(r.text)

            for r in s:
                job = {}
                job['outbreakId'] = r.outbreakId.text
                jobs.append(job)

            # Next page
            pageno += 1
            self.search_request['pageNumber'] = pageno

        return jobs


if __name__ == '__main__':
    scraper = AppleJobsScraper()
    scraper.scrape()