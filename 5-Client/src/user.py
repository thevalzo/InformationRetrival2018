import requests
import MySQLdb
import json
import math

class User():
    user=""

    def __init__(self, user_name):
        self.user=user_name



    def retrive_tweets(self, ids, topic):

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
            query = "SELECT tweet, article  from tweets where usable=true and id_tweet=\'" + str(
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

        #recupera i termini indicizzati
        r = requests.get("http://localhost:8983/solr/"+self.user+"_"+topic+"/terms?terms.fl=article")
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

        print(max_tf)
        for i in terms:

            weights[i]=abs(float(terms[i]['ttf'])/float(max_tf)*math.log(float(1)/float(terms[i]['df'])))
            print(str(i) +" : "+str(weights[i]))


        #salva sul db i pesi calcolati
        for i in weights:
            db = MySQLdb.connect(host="127.0.0.1",
                                 user="root",
                                 passwd="root",
                                 db="information_retrival")


            cursor = db.cursor()
            query = "SELECT id  from personalization where word=\'" + str(i) + "\' and user_name=\'" + str(self.user) + "\' and user_topic=\'" + str(topic) + "\';"
            print(query)
            cursor.execute(query)
            results = cursor.fetchall()

            if(results.__len__()==0):
                cursor = db.cursor()
                query = "INSERT into personalization(user_name, user_topic, word, weight)" \
                        " values(\'" + str(self.user) +"\',\'"+str(topic)+"\',\'"+str(i)+"\',\'"+str(weights[i])+ "\');"
                print(query)
                cursor.execute(query)
                db.commit()
            else:
                for row in results:

                    id=row[0]
                cursor = db.cursor()
                query = "UPDATE personalization SET weight=\'"+str(weights[i])+"\' WHERE id=\'"+ str(id) +  "\';"
                print(query)
                cursor.execute(query)
                db.commit()

    def get_weights(self, topic):
        db = MySQLdb.connect(host="127.0.0.1",
                            user="root",
                             passwd="root",
                             db="information_retrival")


        cursor = db.cursor()
        query = "SELECT word, weight  from personalization where user_name=\'" + str(
            self.user) + "\' and user_topic=\'" + str(topic) + "\';"
        print(query)
        cursor.execute(query)
        results = cursor.fetchall()

        weights={}
        for row in results:
            weights[str(row[0])].append(row[1])

        return weights

def main():
    ids = [
        '943421265238298624',
        '938019396278034432',
        '938417520129728512'
    ]
    #retrive_tweets(ids, "user1", "sport")
    instance= User("user1")
    instance.calculate_weights("sport")
    print(instance.get_weights("sport"))

if __name__ == '__main__':
    main()