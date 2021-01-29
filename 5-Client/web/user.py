from pysolr import Solr
import requests
import MySQLdb
import json
import math
import operator

class User():
    user=""

    def __init__(self, user_name):
        self.user=user_name

    def get_topic(self):
        db = MySQLdb.connect(host="127.0.0.1",
                             user="root",
                             passwd="root",
                             db="information_retrival")

        cursor = db.cursor()
        query = "select user_topic from personalization where user_name=\'"+str(self.user)+"\' group by(user_topic);"
        cursor.execute(query)
        results = cursor.fetchall()

        # Extract topic
        topic=[]
        for row in results:
            topic.append(row[0])

        return topic

    def delete_collection(self, topic):

        #url = "http://localhost:8983/solr/" + str(self.user) + "_" + topic + "/update/json/docs?commit=true"
        #data = {}
        #query["article"]="*:*"
        #data["delete"] = query
        #r = requests.post(url, data=data)
        #print(str(data))
        #print(r.status_code, r.reason)

        conn = Solr('http://localhost:8983/solr/'+ str(self.user) + "_" + topic )

        conn.delete(q='*:*')

        db = MySQLdb.connect(host="127.0.0.1",
                             user="root",
                             passwd="root",
                             db="information_retrival")

        cursor = db.cursor()
        query = "DELETE  from personalization where user_name=\'" + str(self.user) + "\' and user_topic=\'" + str(topic) + "\';"
        print(query)
        cursor.execute(query)
        db.commit()


    def insert_tweets(self, ids, topic):

        #self.delete_collection(topic)

        #retrive texts

        url="http://localhost:8983/solr/"+str(self.user)+"_"+topic+"/update/json/docs?commit=true"


        #print(r.text[:300] + '...')
        db = MySQLdb.connect(host="127.0.0.1",
                                  user="root",
                                  passwd="root",
                                  db="information_retrival")


        data = []

        for id in ids:


            cursor = db.cursor()
            query = "SELECT tweet, article  from tweets where usable=true and id=\'" + str(
                id) + "\' and no_article=FALSE limit 200000;"
            print(query)
            cursor.execute(query)
            results = cursor.fetchall()

            # Extract urls

            for row in results:
                element = {}
                element['tweet'] = row[0]
                element['article'] = row[1]
                data.append(element)

        json_data = json.dumps(data)
        print(json_data)

        r = requests.post(url, data=json_data)
        print(r.status_code, r.reason)


    def calculate_weights(self, topic):



        # recupera il numero di documenti totali
        r = requests.get("http://localhost:8983/solr/" + self.user + "_" + topic + "/select?q=*:*")
        response = r.json()
        tot_doc = response['response']['numFound']

        # CALCOLA I TERMINI PER TWEET
        # recupera i termini indicizzati
        r = requests.get(
            "http://localhost:8983/solr/" + self.user + "_" + topic + "/terms?terms.limit=200&terms.fl=tweet")
        response = r.json()
        terms = response['terms']['tweet']
        # recupera le frequenze per ogni termine
        url = "http://localhost:8983/solr/" + self.user + "_" + topic + "/terms?terms.fl=tweet&terms.list="

        for i in range(0, terms.__len__()):
            if (i % 2 == 0):
                if (terms[i].__len__() > 1):
                    url = url + str(terms[i]) + ","
        url = url[:-1]
        url = url + "&terms.ttf=true"

        r = requests.get(url)
        response = r.json()
        print(response)
        terms = response['terms']['tweet']
        max_tf = 0
        weights = {}

        for i in terms:
            if (terms[i]['ttf'] > max_tf):
                max_tf = terms[i]['ttf']

        print(max_tf)
        for i in terms:
            weights[i] = abs(float(terms[i]['ttf']) / float(max_tf) )
            #* math.log(float(1) / float(terms[i]['df'])))
            print("tweet "+str(i) + " : " + str(weights[i]))

        # salva sul db i pesi calcolati
        for i in weights:
            db = MySQLdb.connect(host="127.0.0.1",
                                 user="root",
                                 passwd="root",
                                 db="information_retrival")

            word = str(i).replace("'", r"\'")
            cursor = db.cursor()
            query = "SELECT id  from personalization where word=\'" + word + "\' and user_name=\'" + str(
                self.user) + "\' and user_topic=\'" + str(topic) + "\' and type='tweet';"
            print(query)
            cursor.execute(query)
            results = cursor.fetchall()

            if (results.__len__() == 0):
                if (weights[i] != 0.0):
                    cursor = db.cursor()

                    query = "INSERT into personalization(user_name, user_topic, word, weight, type)" \
                            " values(\'" + str(self.user) + "\',\'" + str(topic) + "\',\'" + word + "\',\'" + str(
                        weights[i]) + "\', 'tweet');"
                    print(query)
                    cursor.execute(query)
                    db.commit()
            else:
                id = ""
                for row in results:
                    id = row[0]
                    cursor = db.cursor()
                    query = "UPDATE personalization SET weight=\'" + str(weights[i]) + "\' WHERE id=\'" + str(
                        id) + "\';"
                    print(query)
                    cursor.execute(query)
                    db.commit()


        #CALCOLA I TERMINI PER ARTICOLO
        #recupera i termini indicizzati
        r = requests.get("http://localhost:8983/solr/"+self.user+"_"+topic+"/terms?terms.limit=200&terms.fl=article")
        response=r.json()
        terms = response['terms']['article']
        #recupera le frequenze per ogni termine
        url="http://localhost:8983/solr/"+self.user+"_"+topic+"/terms?terms.fl=article&terms.list="


        for i in range(0, terms.__len__()):
            if(i % 2 == 0):
                if(terms[i].__len__()>1):
                    url=url+str(terms[i])+","
        url= url[:-1]
        url=url+"&terms.ttf=true"

        r = requests.get(url)
        response = r.json()
        print(response)
        terms = response['terms']['article']
        max_tf=0
        weights={}

        for i in terms:
            if(terms[i]['ttf']>max_tf):
                max_tf=terms[i]['ttf']


        for i in terms:

            weights[i]=abs(float(terms[i]['ttf'])/float(max_tf)*math.log(float(1)/float(terms[i]['df'])))
            print("article "+str(i) +" : "+str(weights[i]))


        #salva sul db i pesi calcolati
        for i in weights:
            db = MySQLdb.connect(host="127.0.0.1",
                                 user="root",
                                 passwd="root",
                                 db="information_retrival")

            word = str(i).replace("'", r"\'")
            cursor = db.cursor()
            query = "SELECT id  from personalization where word=\'" + word + "\' and user_name=\'" + str(self.user) + "\' and user_topic=\'" + str(topic) + "\'and type='article';"
            print(query)
            cursor.execute(query)
            results = cursor.fetchall()

            if(results.__len__()==0 ):
                if(weights[i]!=0.0):
                    cursor = db.cursor()

                    query = "INSERT into personalization(user_name, user_topic, word, weight, type)" \
                            " values(\'" + str(self.user) +"\',\'"+str(topic)+"\',\'"+word+"\',\'"+str(weights[i])+ "\', 'article');"
                    print(query)
                    cursor.execute(query)
                    db.commit()
            else:
                id=""
                for row in results:

                    id=row[0]
                    cursor = db.cursor()
                    query = "UPDATE personalization SET weight=\'"+str(weights[i])+"\' WHERE id=\'"+ str(id) +  "\';"
                    print(query)
                    cursor.execute(query)
                    db.commit()

    def get_weights(self, topic, tipo):
        db = MySQLdb.connect(host="127.0.0.1",
                            user="root",
                             passwd="root",
                             db="information_retrival")


        cursor = db.cursor()
        query = "SELECT word, weight  from personalization where user_name=\'" + str(
            self.user) + "\' and user_topic=\'" + str(topic) + "\' and type='article' order by weight desc limit 10;"
        print(query)
        cursor.execute(query)
        results = cursor.fetchall()

        weights_article={}
        for row in results:
            weights_article[row[0]]=row[1]

        query = "SELECT word, weight  from personalization where user_name=\'" + str(
            self.user) + "\' and user_topic=\'" + str(topic) + "\' and type='tweet' order by weight desc limit 10;"
        print(query)
        cursor.execute(query)
        results = cursor.fetchall()

        weights_tweet = {}
        for row in results:
            weights_tweet[row[0]] = row[1]

        weights={}
        weights['article']=weights_article
        weights['tweet'] = weights_tweet
        if (tipo=="tweet"):
            return sorted(weights_tweet.items(), key=operator.itemgetter(1), reverse=True)
        if (tipo=="article"):
            return sorted(weights_article.items(), key=operator.itemgetter(1), reverse=True)
def main():
    ids = [
        '50',
        '17984',
        '22668',
        '773385'


                ]

    instance= User("tom")
    #instance.delete_collection("costume_e_societa")
    #instance.delete_collection("cronaca")
    #instance.delete_collection("politica")
    instance.insert_tweets(ids, "cronaca")
    instance.calculate_weights("cronaca")
    #print(instance.get_weights("politica"))
    #instance.delete_collection("sport")

if __name__ == '__main__':
    main()