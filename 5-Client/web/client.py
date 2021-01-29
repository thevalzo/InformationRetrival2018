from flask import Flask, render_template, request, redirect
import sys, os, subprocess
lib_path = os.path.abspath(os.path.join('..', 'src'))
sys.path.append(lib_path)
import urllib
from urlparse import urlparse
import urllib2
from user import User
#from flask_mysqldb import MySQL
#from urllib.request import urlopen

app = Flask(__name__)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/profili/<user_name>')
def user(user_name):
    user=User(user_name)
    return render_template(user_name+'.html')

@app.route('/<user_name>/ricerca')
def userSearch(user_name):
    #user_name="user1"
    user=User(user_name)
    return render_template('ricerca.html', user=user_name, topic= user.get_topic())

@app.route('/<user_name>/ricerca', methods=['POST', 'GET'])
def search(user_name):
    query=""
    url=""
    if request.method == 'POST':
        query = str(request.form['query'])
        user=User(user_name)
        topic = str(request.form.get('box_interessi'))

        url = "http://localhost:8983/solr/demo/select?q="

        if (request.form.get('boost')=='recency'):
            # if(request.form.getlist('cb1')[0]=="yes"):
            url = url + "{!boost%20b=tweet_date}"
        if (request.form.get('boost')=='popularity'):
            # if(request.form.getlist('cb1')[0]=="yes"):
            url = url + "{!boost%20b=favourite_count}"
        print(str(topic)+" not equal "+str(topic)+" = "+str(str(topic).__eq__("nessuno")))
        if (str(topic).__eq__("nessuno") != True):
            weights=user.get_weights(topic, "tweet")
            personalized_terms=" "
            print("topic: "+str(request.form.get('topic_list')))
            for i in weights:
                personalized_terms=personalized_terms+" and article:\""+str(i[0])+"\"^"+str(i[1])

            url = url + "(tweet:\"" + query + "\"^3 and article:\"" + query+"\"^3 "+personalized_terms+")"
            print("url:  "+str(url))
        else:
            url = url + "(tweet:\"" + query + "\"^3 and article:\"" + query + "\"^3)"
            print("url:  " + str(url))

    #connection = urlopen('http://localhost:8983/solr/demo/select?q=tweet:lamborghini%20ursus')
    connection = urllib.urlopen(url)
    response = eval(connection.read())

    #print(str(response['response']['numFound'])+"documents found.")

    # Print the name of each document.
    result=[]
    element=[]
    screen_name=[]
    article=[]
    for document in response['response']['docs']:
        element = []
        element.append(document['tweet'])
        element.append(document['tweet_date'][:10])
        element.append(document['screen_name'][0])
        element.append(document['url'][0])
        if('article' in document.keys()):
            element.append(document['article'][:200]+".....")
        else:
            element.append("")


        element.append(document['favourite_count'])
        result.append(element)

    return render_template('ricerca.html', result=result, user=user.user ,topic=user.get_topic())

@app.route('/<user_name>/clicked', methods=['POST', 'GET'])
def clicked_result(user_name):
    user=User(user_name)
    print("user "+user_name+" clicked "+ request.form['url'])

    return redirect(request.form['url'])

#******** OLD
@app.route('/<user_name>')
def userold(user_name):
    user=User(user_name)
    return render_template('index.html', user=user_name, topic= user.get_topic())

@app.route('/search', methods=['POST', 'GET'])
def searchold():
    query=""
    url=""
    if request.method == 'POST':
        query = str(request.form['query'])
        user_name = str(request.form['user'])
        user=User(user_name)
        topic = str(request.form.get('topic_list'))

        url = "http://localhost:8983/solr/demo/select?q="

        checked1 = 'cb1' in request.form
        checked2 = 'cb2' in request.form

        if (checked1):
            # if(request.form.getlist('cb1')[0]=="yes"):
            url = url + "{!boost%20b=tweet_date}"
        if (checked2):
            # if(request.form.getlist('cb1')[0]=="yes"):
            url = url + "{!boost%20b=favourite_count}"

        if topic != "/":
            weights=user.get_weights(topic)
            personalized_terms=" "
            print("topic: "+str(request.form.get('topic_list')))
            for i in weights:
                personalized_terms=personalized_terms+" or article:\""+str(i[0])+"\"^"+str(i[1])

            url = url + "tweet:\"" + urllib.pathname2url(query) + "^5\"article:\"" + query+"\"^5"+personalized_terms

        else:
            url = url + "tweet:\"" + urllib.pathname2url(query) + "^5\"article:\"" + query + "^5\""

        print("url:  " + str(url))

    #connection = urlopen('http://localhost:8983/solr/demo/select?q=tweet:lamborghini%20ursus')
    connection = urllib.urlopen(url)
    response = eval(connection.read())

    #print(str(response['response']['numFound'])+"documents found.")

    # Print the name of each document.
    result=[]
    element=[]
    screen_name=[]
    article=[]
    for document in response['response']['docs']:
        element = []
        element.append(document['tweet'])
        element.append(document['tweet_date'][:10])
        element.append(document['screen_name'][0])
        element.append(document['url'][0])
        if('article' in document.keys()):
            element.append(document['article'][:200]+".....")
        else:
            element.append("")

        element.append(document['retweet_count'])
        element.append(document['favourite_count'])
        result.append(element)

    return render_template('index.html', result=result, user=user.user ,topic=user.get_topic())

if __name__ == '__main__':
    app.debug = True
    app.run()
