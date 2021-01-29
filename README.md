0-PYTHON----------------------------------------
La versione installata richiesta per python è la 2.7
Per eseguire i file da linea di comando è necessario 
impostare le variabili d'ambiente

1-DATABASE----------------------------------------
Lo schema va chiamato information_retrival
Il server SQL è all'indirizzo localhost:3306
user:root
password:root

2-CRAWLER-----------------------------------------
Per eseguire il crawler  servono le  librerie tweepy, mysqdb:
cmd > pip install tweepy
cmd > pip install python-mysqldb
poi è sufficiente posizionarsi nella cartella del file.py:
cmd > python crawler.py

3-SPYDERS-----------------------------------------
Per eseguire gli spyders servono le librerie scrapy, beautifulsoup:
cmd > pip install scrapy
cmd > pip install bs4
poi è sufficiente posizionarsi nella cartella spyders all'interno del progetto scrapy
cmd > scrapy crawl cor
cmd > scrapy crawl rep
cmd > scrapy crawl others

4-SOLR--------------------------------------------
Per importare i core è sufficiente posizionare la cartella solr, 
contenente i core, in solr>server>solr
Invece la cartella dataimporthandler va posizionata in solr>contrib
Per eseguire solr:
cmd > \solr\bin>solr start
Il server solr dovrà essere visibile all'indirizzo http://localhost:8983

5-CLIENT------------------------------------------
Per eseguire gli spyders servono le librerie flask, pysolr
cmd > pip install scrapy
cmd > pip install bs4
poi è sufficiente posizionarsi nella cartella web py:
cmd > python client.py
L'interfaccia è visibile all'indirizzo http://127.0.0.1:5000/