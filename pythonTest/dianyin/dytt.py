#!/usr/bin/env python
#coding=utf-8

import re
from bs4 import BeautifulSoup
from urllib import parse,request

class dytt8(object):
    def __init__(self, num):
        self.num = num

    def list_url(self):
        tmp_url = []
        host_prefix = 'http://www.dytt8.net/html/gndy/dyzz/'
        tmp_url = [host_prefix + 'index.html']

        for i in range(1,self.num):
            tmp_url.append(host_prefix + 'list_23_' + str(i) + '.html')
        return  tmp_url

    def http_url(self):
        url_to_work = []
        host = 'http://www.dytt8.net'
        for u in self.list_url():
            try:
                data = request.urlopen(u).read().decode('gbk', 'ignore')
                data.encode('utf-8')
            except:
                pass
            try:
                soup = BeautifulSoup(data)
                link = soup.find('div', {"class":"co_content8"})
                for url in link.findAll('a', {"class":"ulink"}):
                    url_to_work.append(host+url['href'])
            except:
                pass
        return url_to_work

    def ftp_url(self, url):
        ftp_link = ''
        try:
            data = request.urlopen(url).decode('gbk', 'ignore').encode('utf-8')
            res = re.compile(r'(ftp://.*?\.rmvb)')
            try:
                ftp_link = str(res.findall(str(data))[0]).decode('utf-8')
            except:
                pass
        except:
            pass
        return ftp_link

if __name__ == '__main__':
    t = dytt8(30)
    for url in t.http_url():
        f = open('url.text', 'w')
        f.write(url)
        f.close()
        print(url)