import scrapy
import unidecode
import MySQLdb
import re
import datetime

from bs4 import BeautifulSoup


class repubblicaSpider(scrapy.Spider):
    name = "others"
    db = ""
    id_tweet = 0
    updated = 0
    empty = 0
    list = []
    urls = []
    ids=[
        #'18935802',
        #'395218906',
        '29416653',
        '420351046',
        '150725695'
    ]

    def start_requests(self):

        self.id = 0
        self.updated = 0
        self.empty = 0
        self.list = []
        self.urls = []
        self.source = []

        # Connect to DB
        self.db = MySQLdb.connect(host="127.0.0.1",
                                  user="root",
                                  passwd="root",
                                  db="information_retrival")

        for id in self.ids:



            cursor = self.db.cursor()
            query="SELECT url, id_tweet, id_source  from tweets where usable=true and id_source=\'"+str(id)+"\' and article IS NULL and url IS NOT NULL and no_article=FALSE limit 200000;"
            print(query)
            cursor.execute(query)
            results = cursor.fetchall()

            # Extract urls

            for row in results:
                self.urls.append(row[0])
                self.list.append(row[1])
                self.source.append(row[2])

            # Call scrapy for every urls
            for i in range(0, self.urls.__len__()):


                file = open("C:\Users\marco\PycharmProjects\Crawler\crawler\crawler\log" + str(
                    datetime.datetime.now().strftime("%Y-%m-%d")) + ".txt", "w")
                file.write("Available urls: " + str(self.urls) + "\n")
                file.write("N* urls: " + str(self.urls.__len__()) + "\n")
                file.write("N* ids: " + str(self.list.__len__()) + "\n")
                file.write("N* inserted: " + str(self.updated) + "\n")
                file.write("N* empty: " + str(self.empty) + "\n")
                file.close()

                yield scrapy.Request(url=self.urls[i], callback=self.parse, meta={'dont_merge_cookies': True, 'id': self.list[i], 'source' : self.source[i] })

    def parse(self, response):

        # extract text
        text = ""
        list = []
        body = response.body
        source = response.meta.get('source')
        soup = BeautifulSoup(body, 'html.parser' ,  from_encoding='ISO-Latin-1')

        [s.extract() for s in soup('script')]
        [s.extract() for s in soup('style')]

        id = response.meta.get('id')

        if(source==18935802): #Repubblica
            list = soup.findAll("span", {"itemprop": "articleBody"})
            if (not list):
                list = soup.findAll("p", {"class": "wp-caption-text"})
            if (not list):
                list = soup.findAll("span", {"itemprop": "description"})



        elif(source==29416653): #LaStampa
            list = soup.findAll("div", {"itemprop": "articleBody"})

        elif (source == 395218906): #Corriere
            list = soup.findAll("p", {"class": "wp-caption-text"})
            if (not list):
                list = soup.findAll("h6", {"class": "chapter-description"})
            if (not list):
                list = soup.findAll("div", {"itemprop": "articleBody"})
            if (not list):
                list = soup.findAll("p", {"class": "chapter-paragraph"})
            if (not list):
                list = soup.findAll("div", {"class": "text"})
            if (not list):
                list = soup.findAll("div", {"class": "chapter"})
            if (not list):
                list = soup.findAll("p", {"class": "article-subtitle"})

        elif (source == 150725695): #Ansa
            [s.extract() for s in soup('a')]
            [s.extract() for s in soup('strong')]

            list = soup.findAll("div", {"itemprop": "articleBody"})

        elif (source == 420351046): #Sole24
            [s.extract() for s in soup('script')]
            [s.extract() for s in soup('style')]
            [s.extract() for s in soup('a')]
            [s.extract() for s in soup('h4')]
            [s.extract() for s in soup('h5')]
            [s.extract() for s in soup('time')]
            [s.extract() for s in soup("p", {"class": "reserved"})]
            [s.extract() for s in soup("footer", {"class": "article-footer"})]

            list = soup.findAll("div", {"id": "article-body"})
            list += soup.findAll("div", {"class": "article-content"})
        else:
            file = open("C:\Users\marco\PycharmProjects\Crawler\crawler\crawler\logx" + str(
                datetime.datetime.now().strftime("%Y-%m-%d")) + ".txt", "a")
            file.write(" NO MATCH \n")
            file.close()

        if (not list):
            page = response.url.split("/")[-2]
            filename = str(source)+'/raw-file-%s.html' % page
            with open(filename, 'a') as f:
                f.write(body)
            self.log('Saved file %s' % filename)
            f.close

            cursor = self.db.cursor()
            query = "UPDATE tweets SET no_article=1 WHERE id_tweet=\'" + str(id) + "\';"
            print(query)
            cursor.execute(query)
            self.db.commit()

        for item in list:
            text += unidecode.unidecode(item.get_text())
        text = filter(lambda x: not re.match(r'^\n*$', x), text)



        # Create text file
        if (text.__len__() != 0):
            cursor = self.db.cursor()
            query = "UPDATE tweets SET article=\'" + str(text).replace('\"', '\\\"').replace('\'',
                                                                                             '\\\'') + "\'WHERE id_tweet=\'" + str(
                id) + "\';"

            cursor.execute(query)
            self.db.commit()
            self.updated += 1


