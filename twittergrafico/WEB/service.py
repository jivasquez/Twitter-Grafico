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
from twittergrafico.WEB.lib import auth, passhash, render

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
#SIGNIN_URL        = 'https://api.twitter.com/oauth/authenticate'
CONSUMER_KEY='H8XJeW1h6f8pdFcdWqlA'
CONSUMER_SECRET='N0FIYX4jHZzovkpVLTjSrf3M7kf0PdyHHgW1r0xQ6o'

@route('/static/<path:path>')
def static(path):
    ASSETS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    return static_file(path, ASSETS_PATH)

@route('/')
@route('/home')
def home():
    return render('templates/home.html')

@route('/list')
@auth()
def list(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    filtered_messages = []
    for index, message in enumerate(messages):
        if  Filter.image_filter(message):
            filtered_messages.append(messages[index])
    return render('templates/list.html', messages=filtered_messages)


@route('/clustered_tweets')
@auth()
def clustered(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    clustering = Clustering(messages, user)
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return render('templates/clustered_list.html', clusters=clusters, representative=seleccion.representative_tweets, messages=messages)

    
@route('/clustered_keywords')
@auth()
def keywords(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    clustering = Clustering(messages, user, 'keywords')
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return render('templates/clustered_list.html', clusters=clusters, representative=seleccion.representative_tweets, messages=messages)
    
@route('/maxtf')
@auth()
def maxtf(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    clustering = Clustering(messages, user, 'keywords', rowmodel='maxtf')
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return render('templates/clustered_list.html', clusters=clusters, representative=seleccion.representative_tweets, messages=messages)

@route('/search')
def search():
    query = request.GET.get('q')
    messages = Twitter_DAO.get_messages_from_search(query)
    filtered_messages = []
    for index, message in enumerate(messages):
        if  Filter.image_filter(message):
            filtered_messages.append(messages[index])
    return render('templates/list.html', messages=filtered_messages)

    
@route('/register')
def register():
    return render('templates/register.html')
    
@route('/register_account', method='POST')
def register_account():
    username = request.POST.get('username')
    password = request.POST.get('password')
    repeat = request.POST.get('repeat')
    if len(username) < 6 or password != repeat or len(password)< 6:
        return render('templates/register.html')
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
    print access_token
    session = hashlib.sha256(access_token.get('oauth_token') + str(random.random())).hexdigest()
    response.set_cookie("t", session, path='/')
    key = request.get_cookie('k')
    response.delete_cookie('k')
    user = Account.get_user_from_key(key)
    user.oauth_token = access_token.get('oauth_token')
    user.oauth_token_secret = access_token.get('oauth_token_secret')
    user.user_id = access_token.get('user_id')
    user.screen_name = access_token.get('screen_name')
    user.session = session
    user.save()
    redirect('/home')
    
@route('/logout')
def logout():
    response.delete_cookie('t')
    redirect('/')

bottle.debug(True)
run(host='0.0.0.0', port=8080, reloader=True)