# -*- coding: utf-8 -*-
import os
import urllib
import random
import hashlib

from bottle import route, run, static_file, request, redirect, response
import bottle
from bottle import mako_view as view, mako_template as template
try:
  from urlparse import parse_qsl
except:
  from cgi import parse_qsl
import oauth2 as oauth

from twittergrafico.agrupacion import Clustering
from twittergrafico.seleccion import Seleccion
from twittergrafico.tweets import Twitter_DAO
from twittergrafico.filter import Filter
from twittergrafico.account import Account
from twittergrafico.WEB.lib import auth, passhash, render, get_json_from_clusters, get_json_from_list

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
CONSUMER_KEY='H8XJeW1h6f8pdFcdWqlA'
CONSUMER_SECRET='N0FIYX4jHZzovkpVLTjSrf3M7kf0PdyHHgW1r0xQ6o'

@route('/static/<path:path>')
def static(path):
    ASSETS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    return static_file(path, ASSETS_PATH)

@route('/')
@route('/home')
def home():
    return render('home.html')

@route('/list', method='POST')
@auth()
def list(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    filtered_messages = []
    for index, message in enumerate(messages):
        if  Filter.image_filter(message):
            filtered_messages.append({"message":message.message, "id":message.id, "url":message.url, "image":message.image, "massive":message.massive})
    return {"messages":filtered_messages}

@route('/list', method='GET')    
@auth()
def list(user):
    return render('list.html')

@route('/clustered_tweets')
@route('/clustered_keywords')
@route('/maxtf')
@route('/clustered_text')
@auth()
def clustered(user):
    return render('clustered_list.html')

@route('/clustered_tweets', method='POST')
@auth()
def clustered(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    clustering = Clustering(messages, user)
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return {"clusters": get_json_from_clusters(clusters), "representative":get_json_from_list(seleccion.representative_tweets)}

    
@route('/clustered_keywords', method='POST')
@auth()
def keywords(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    clustering = Clustering(messages, user, 'keywords')
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return {"clusters": get_json_from_clusters(clusters), "representative":get_json_from_list(seleccion.representative_tweets)}
    
@route('/maxtf', method='POST')
@auth()
def maxtf(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    clustering = Clustering(messages, user, 'keywords', rowmodel='maxtf')
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return {"clusters": get_json_from_clusters(clusters), "representative":get_json_from_list(seleccion.representative_tweets)}

@route('/clustered_text', method='POST')
@auth()
def clustered_text(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    clustering = Clustering(messages, user, 'text', rowmodel='maxtf')
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return {"clusters": get_json_from_clusters(clusters), "representative":get_json_from_list(seleccion.representative_tweets)}

@route('/search')
def search():
    return "Not available right now"
    query = request.GET.get('q')
    messages = Twitter_DAO.get_messages_from_search(query)
    filtered_messages = []
    for index, message in enumerate(messages):
        if  Filter.image_filter(message):
            filtered_messages.append(messages[index])
    return render('list.html', messages=filtered_messages)

    
@route('/register')
def register():
    return render('register.html')
    
@route('/register_account', method='POST')
def register_account():
    username = request.POST.get('username')
    password = request.POST.get('password')
    repeat = request.POST.get('repeat')
    if len(username) < 6 or password != repeat or len(password)< 6:
        return render('register.html')
    else:
        user = User(username, passhash(password))
        # this key is used once on the registration to know who was the user trying to authenticate with Twitter
        user.key = hashlib.sha256(username + password).hexdigest()
        user.save()
        response.set_cookie("k", user.key, path='/')
        oauth_consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
        oauth_client = oauth.Client(oauth_consumer)
        resp, content = oauth_client.request(REQUEST_TOKEN_URL, 'POST', body=urllib.urlencode({'oauth_callback':'http://localhost:8080/end_registration'}))
        request_token = dict(parse_qsl(content))
        url = "%s?oauth_token=%s" % (AUTHORIZATION_URL, request_token['oauth_token']) 
        redirect(url)

@route('/login', method="POST")
def get_login_url():
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = Account.get_user(username)
    if user:
        if user.password != passhash(password):
            redirect('home')
        else:
            user.login()
            response.set_cookie("t", user.session, path='/')
    redirect('home')

@route('/end_registration')
def end_registration():
    oauth_token = request.GET.get('oauth_token')
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    oauth_client = oauth.Client(oauth_consumer)
    resp, content = oauth_client.request(ACCESS_TOKEN_URL, 'POST', body=urllib.urlencode({'oauth_token':oauth_token, 'oauth_verifier':oauth_verifier}))
    access_token  = dict(parse_qsl(content))
    key = request.get_cookie('k')
    response.delete_cookie('k')
    user = Account.get_user_from_key(key)
    user.oauth_token = access_token.get('oauth_token')
    user.oauth_token_secret = access_token.get('oauth_token_secret')
    user.user_id = access_token.get('user_id')
    user.screen_name = access_token.get('screen_name')
    user.save()
    user.login()
    response.set_cookie("t", user.session, path='/')
    redirect('/home')
    
@route('/logout')
@auth()
def logout(user):
    user.logout()
    response.delete_cookie('t')
    redirect('/')
    
    
    
#Testing purposes
@route('/test_clusters')
@auth()
def test_clusters(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    file = open("/Users/juan/desktop/prueba.txt", 'w')
    clustering = Clustering(messages, user, 'keywords', rowmodel='maxtf', clmethod='rb')
    file.write(unicode("Resultados de clustering para -clmethod=rb\n").encode("utf-8"))
    for index, cluster in enumerate(clustering.clusters):
        file.write(unicode(u"Cluster Nº" + str(index + 1) + "\n").encode("utf-8"))
        for tweet in cluster:
            file.write(unicode(tweet.message + "\n").encode("utf-8"))

    clustering = Clustering(messages, user, 'keywords', rowmodel='maxtf', clmethod='rbr')
    file.write(unicode("Resultados de clustering para -clmethod=rbr\n").encode("utf-8"))
    for index, cluster in enumerate(clustering.clusters):
        file.write(unicode(u"Cluster Nº" + str(index + 1) + "\n").encode("utf-8"))
        for tweet in cluster:
            file.write(unicode(tweet.message + "\n").encode("utf-8"))

    clustering = Clustering(messages, user, 'keywords', rowmodel='maxtf', clmethod='direct')
    file.write(unicode("Resultados de clustering para -clmethod=direct\n").encode("utf-8"))
    for index, cluster in enumerate(clustering.clusters):
        file.write(unicode(u"Cluster Nº" + str(index + 1) + "\n").encode("utf-8"))
        for tweet in cluster:
            file.write(unicode(tweet.message + "\n").encode("utf-8"))

    clustering = Clustering(messages, user, 'keywords', rowmodel='maxtf', clmethod='agglo')
    file.write(unicode("Resultados de clustering para -clmethod=agglo\n").encode("utf-8"))
    for index, cluster in enumerate(clustering.clusters):
        file.write(unicode(u"Cluster Nº" + str(index + 1) + "\n").encode("utf-8"))
        for tweet in cluster:
            file.write(unicode(tweet.message + "\n").encode("utf-8"))

    clustering = Clustering(messages, user, 'keywords', rowmodel='maxtf', clmethod='graph')
    file.write(unicode("Resultados de clustering para -clmethod=graph\n").encode("utf-8"))
    for index, cluster in enumerate(clustering.clusters):
        file.write(unicode(u"Cluster Nº" + str(index + 1) + "\n").encode("utf-8"))
        for tweet in cluster:
            file.write(unicode(tweet.message + "\n").encode("utf-8"))

    clustering = Clustering(messages, user, 'keywords', rowmodel='maxtf', clmethod='bagglo')
    file.write(unicode("Resultados de clustering para -clmethod=bagglo\n").encode("utf-8"))
    for index, cluster in enumerate(clustering.clusters):
        file.write(unicode(u"Cluster Nº" + str(index + 1) + "\n").encode("utf-8"))
        for tweet in cluster:
            file.write(unicode(tweet.message + "\n").encode("utf-8"))


    return "Done"

bottle.debug(True)
run(host='0.0.0.0', port=8080, reloader=True)