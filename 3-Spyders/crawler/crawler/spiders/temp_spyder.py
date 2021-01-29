import scrapy
import unidecode
import MySQLdb
import re
import chardet
from bs4 import BeautifulSoup

class QuotesSpider(scrapy.Spider):
    name = "test"

    def start_requests(self):

        urls = ['https://t.co/NmVxC2Q4jv']
        for url in urls:

            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        response_n=""
        response_n=response.replace(encoding='utf-8')
        text=""
        body =  response_n.body
        page =  response_n.url.split("/")[-2]
        filename = 'araw-test-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(body)
        self.log('Saved file %s' % filename)
        f.close


        soup = BeautifulSoup(body, "html.parser", from_encoding='ISO-Latin-1')
        [s.extract() for s in soup('script')]
        list = soup.findAll("div", {"class": "text"})
        print("test1:"+str(list))
        print("test:" + str(not list))
        if (not list):
            list = soup.findAll("h6", {"class": "chapter-description"})
            print("test2:" + str(list))
            print("test:" + str(not list))
        if (not list):
            list = soup.findAll("p", {"class": "chapter-paragraph"})
            print("test3:" + str(list))
            print("test:" + str(not list))
        if (not list):
            list = soup.findAll("div", {"itemprop": "articleBody"})
            print("test4:" + str(list))
            print("test:" + str(not list))
        if (not list):
            list = soup.findAll("div", {"class": "text"})
            print("test6:" + str(list))
            print("test:" + str(not list))
        print("final:" + str(list))
        print("test:" + str(not list))
        for item in list:
            text += unidecode.unidecode(item.get_text())
        text = filter(lambda x: not re.match(r'^\n*$', x), text)

        filename = 'atext-test-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(text)
        self.log('Saved file %s' % filename)
        f.close
        