import tweepy
import _mysql
import MySQLdb
import unidecode
import re
import json
import datetime
def  main():


    # Connecssione al DB Sql
    db = MySQLdb.connect(host="127.0.0.1",
                         user="root",
                         passwd="root",
                         db="information_retrival")

    with open('..\connection.json', 'w') as file:
        data = json.load(file)

    # Setup API

    auth = tweepy.OAuthHandler(data["OAuthHandler"][0], data["OAuthHandler"][1])
    auth.set_access_token(data["AccessToken"][0],data["AccessToken"][1])

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    news_sources = ["Corriere", "repubblica", "LaStampa", "Agenzia_Ansa", "sole24ore"]

    file = open("D:\Universita\Information_Retrival\Progetto\log"+str(datetime.datetime.now().strftime("%Y-%m-%d"))+".txt", "a")
    file.write("Current time:"+str(datetime.datetime.now().strftime("%H:%M"))+"\n")

    for source in news_sources:

        duplicate = False
        update_n = 0
        exception = 0
        inserted=0
        query=""
        tweet_plain=""
        most_old = "999999999999999999"
        new_most_old = "999999999999999999"

        public_tweets = api.user_timeline(screen_name=source, count=200)

        # prepare a cursor object using cursor() method

        for tweet in public_tweets:
            #print(str(tweet.id) + " < " + str(new_most_old))
            if (str(tweet.id) < new_most_old):
                new_most_old = tweet.id

            if (tweet.text[:2] != 'RT' and tweet.text!=""):
                # Execute SQL SELECT  statement
                text=""
                try:



                    url=""
                    url=re.findall(r"http\S+", tweet.text)
                    if (url):
                        url = unidecode.unidecode(url[0])
                        url = re.escape(url)

                    text = re.sub(r"http\S+", "", tweet.text)
                    text = unidecode.unidecode(text)
                    text = re.escape(text)

                    plain_tweet=unidecode.unidecode(tweet.text)
                    plain_tweet = re.escape(plain_tweet)
                    hashtags=""
                    if(hasattr(tweet, 'hashtags')):
                        hashtags=tweet.hashtags
                        print(str(tweet.hashtags))

                    n_duplicate=0
                    cursor = db.cursor()
                    query = "SELECT id_tweet FROM tweets WHERE tweet =\'" + str(text) + "\' AND id_tweet <>\'" + str(
                        tweet.id) + "\';"

                    cursor.execute(query)

                    if(cursor.rowcount==0 and text!='\ '):
                        cursor = db.cursor()
                        query = "INSERT INTO tweets (id_tweet, tweet,id_source, tweet_date, favourite_count, screen_name, retweet_count, hashtags, url, plain_tweet) VALUES(\'" + str(tweet.id) + "\',\'" + str(text) + "',\'" + str(tweet.user.id) +"',\'" + str(tweet.created_at) + "',\'" + str(tweet.favorite_count) +"',\'" + source + "',\'" + str(tweet.retweet_count) + "',\'" + str(hashtags) + "',\'" + str(url) + "',\'" + str(plain_tweet)+"');"
                        cursor.execute(query)
                        db.commit()
                        inserted += 1
                    else:
                        n_duplicate+=1




                except  Exception, e:

                    if(e[0]==1062):
                        update_n+=1

                        cursor = db.cursor()
                        query = "UPDATE tweets SET retweet_count=\'"+ str(tweet.retweet_count)+"\' AND favourite_count=\'"+ str(tweet.favorite_count)+"\' WHERE id_tweet=\'"+ str(tweet.id)+"\';"
                        cursor.execute(query)
                        #only for new field
                        cursor = db.cursor()
                        query = "UPDATE tweets SET hashtags=\'" + str(
                            hashtags) + "\', url=\'" + str(
                            url) + "\', plain_tweet=\'" + str(
                            plain_tweet) + "\' WHERE id_tweet=\'" + str(tweet.id) + "\';"
                        cursor.execute(query)
                        db.commit()
                    else:
                        print(e)
                        exception+=1

        # Close the connection
        db.commit()


        #print(str(most_old) + " != " + str(new_most_old) + " : " + str(most_old != new_most_old))
        while (len(public_tweets)!=0 and most_old!=new_most_old):
            #print(str(most_old) + " != " + str(new_most_old)+" : "+str(most_old!=new_most_old))
            # Retrieve most recent tweet
            #try:
            #    query = "SELECT min(id_tweet) FROM information_retrival.tweets WHERE screen_name=\'"+source+"';"
            #    cursor.execute(query)
            #    most_old=new_most_old
            #    new_most_old= cursor.fetchone()[0]
            #   print(str(most_old)+" != "+str(new_most_old))

            #except Exception, e:
            #    print(e)

            # Most old tweet
            most_old = new_most_old
            #print("The most old tweet of "+source+" is: "+str(most_old))

            try:
                public_tweets = api.user_timeline(screen_name=source, count=200, max_id=most_old)
            except:
                print(tweepy.TweepError.message)
            if(len(public_tweets)!=0):
                for tweet in public_tweets:
                    if (tweet.text[:2] != 'RT' and tweet.text!=""):

                        url = ""
                        url = re.findall(r"http\S+", tweet.text)
                        if(url):
                            url = unidecode.unidecode(url[0])
                            url = re.escape(url)

                        text = re.sub(r"http\S+", "", tweet.text)

                        text = unidecode.unidecode(text)
                        text = re.escape(text)

                        plain_tweet = unidecode.unidecode(tweet.text)
                        plain_tweet = re.escape(plain_tweet)
                        hashtags = ""
                        if (hasattr(tweet, 'hashtags')):
                            hashtags = tweet.hashtags
                            print(str(hashtags))

                        if (tweet.id < most_old):
                            new_most_old= tweet.id
                        try:

                            cursor = db.cursor()
                            query = "SELECT id_tweet FROM tweets WHERE tweet =\'" + str(text) + "\' AND id_tweet <>\'" + str(tweet.id) + "\';"

                            cursor.execute(query)




                            if (cursor.rowcount == 0 and text!='\ '):
                                cursor = db.cursor()
                                query = "INSERT INTO tweets (id_tweet, tweet,id_source, tweet_date, favourite_count, screen_name, retweet_count, hashtags, url, plain_tweet) VALUES(\'" + str(
                                    tweet.id) + "\',\'" + str(text) + "',\'" + str(tweet.user.id) + "',\'" + str(
                                    tweet.created_at) + "',\'" + str(
                                    tweet.favorite_count) + "',\'" + source + "',\'" + str(
                                    tweet.retweet_count) + "',\'" + str(hashtags) + "',\'" + str(url) + "',\'" + str(
                                    plain_tweet) + "');"
                                cursor.execute(query)
                                db.commit()
                                inserted += 1
                            else:
                                n_duplicate += 1


                        except  Exception, e:
                            if (e[0] == 1062):
                                duplicate = True
                                update_n += 1
                                cursor = db.cursor()
                                query = "UPDATE tweets SET retweet_count=\'" + str(tweet.retweet_count) + "\' AND favourite_count=\'" +  str(tweet.favorite_count) + "\' WHERE id_tweet=\'" +  str(tweet.id) + "\';"
                                cursor.execute(query)
                                # only for new field
                                cursor = db.cursor()
                                query = "UPDATE tweets SET hashtags=\'" + str(
                                    hashtags) + "\', url=\'" + str(
                                    url) + "\', plain_tweet=\'" + str(
                                    plain_tweet) + "\' WHERE id_tweet=\'" + str(tweet.id) + "\';"
                                cursor.execute(query)
                                db.commit()
                            else:
                                print(e)
                                exception += 1
                                print(query)
            else:
                print("All older tweet retrived")
                duplicate=True
        print("Crawling for "+source+" terminated with " + str(inserted) + " inserted record, " + str(update_n) + " updated and " + str(exception) + " exceptions")
        print("Avoided "+str(n_duplicate)+" duplicated tweet for " + source + "\n")

        file.write("Crawling for "+source+" terminated with " + str(inserted) + " inserted record, " + str(update_n) + " updated and " + str(exception) + " exceptions\n")
        file.write("Avoided "+str(n_duplicate)+" duplicated tweet for " + source + "\n")

    file.write("---------------------------------------------------------------------------------------\n")
    file.close()

    db.close()


if __name__ == "__main__":
    main()