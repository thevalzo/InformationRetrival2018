import scrapy
import unidecode
import MySQLdb
from bs4 import BeautifulSoup

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = []
        db = MySQLdb.connect(host="127.0.0.1",
                             user="root",
                             passwd="root",
                             db="information_retrival")

        cursor = db.cursor()


        cursor.execute("SELECT url  from tweets where usable=true and id_source='395218906' limit 20;")

        results = cursor.fetchall()
        for row in results:
            urls.append(row[0])
        print(urls)
        #urls = ['https://t.co/WOHDV7FOPY']
        for url in urls:

            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-raw-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        f.close
        text=""
        soup = BeautifulSoup(response.body, 'html.parser')

        [s.extract() for s in soup('script')]

        list = soup.findAll("div", {"itemprop": "articleBody"})
        if (not list):
            list = soup.findAll("p", {"class": "chapter-paragraph"})
        elif (not list):
            list = soup.findAll("p", {"class": "article-subtitle"})
        elif (not list):
            list = soup.findAll("h6", {"class": "chapter-description"})
        elif (not list):
            list = soup.findAll("h5", {"class": "chapter-subtitle"})
        for item in list:
            text+=unidecode.unidecode(item.get_text())

        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % unidecode.unidecode(soup.findAll("title", {"itemprop": "name"})[0].get_text().replace("<", "").replace("<", "")[:20])
        with open(filename, 'wb') as f:
            f.write(text)
        self.log('Saved file %s' % filename)

