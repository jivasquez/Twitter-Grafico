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
from twittergrafico.user import User

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
    return template('templates/home.html', asd='asd')

def auth():
    def decorator(view):
        def wrapper(*args, **kwargs):
            session = request.get_cookie('t')
            user = User.get_user_from_session_id(session)
            if user:
                return view(user, *args, **kwargs)
            return bottle.redirect('/login')
        return wrapper
    return decorator
 

@route('/list')
@auth()
def list(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    filtered_messages = []
    for index, message in enumerate(messages):
        if  Filter.image_filter(message):
            filtered_messages.append(messages[index])
    return template('templates/list.html', messages=filtered_messages)


@route('/clustered_tweets')
@auth()
def clustered(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    clustering = Clustering(messages, user)
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return template('templates/clustered_list.html', clusters=clusters, representative=seleccion.representative_tweets, messages=messages)

    
@route('/clustered_keywords')
@auth()
def keywords(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    clustering = Clustering(messages, user, 'keywords')
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return template('templates/clustered_list.html', clusters=clusters, representative=seleccion.representative_tweets, messages=messages)
    
@route('/maxtf')
@auth()
def maxtf(user):
    messages = Twitter_DAO.get_twitter_messages(user, 50)
    clustering = Clustering(messages, user, 'keywords', rowmodel='maxtf')
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return template('templates/clustered_list.html', clusters=clusters, representative=seleccion.representative_tweets, messages=messages)
    
@route('/register')
def register():
    return template('templates/register.html')

@route('/login')
def get_login_url():
    oauth_consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    oauth_client = oauth.Client(oauth_consumer)
    #requesting temp token
    resp, content = oauth_client.request(REQUEST_TOKEN_URL, 'POST', body=urllib.urlencode({'oauth_callback':'http://www.twittergrafico.com/login_url'}))
    request_token = dict(parse_qsl(content))
    print resp, content
    url = "%s?oauth_token=%s" % (AUTHORIZATION_URL, request_token['oauth_token']) 
    redirect(url)

@route('/login_url')
def login():
    oauth_token = request.GET.get('oauth_token')
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    oauth_client = oauth.Client(oauth_consumer)
    resp, content = oauth_client.request(ACCESS_TOKEN_URL, 'POST', body=urllib.urlencode({'oauth_token':oauth_token, 'oauth_verifier':oauth_verifier}))
    access_token  = dict(parse_qsl(content))
    print access_token
    session = hashlib.sha256(access_token.get('oauth_token') + str(random.random())).hexdigest()
    response.set_cookie("t", session, path='/')
    user = User(access_token.get('oauth_token'), access_token.get('oauth_token_secret'), access_token.get('user_id'), access_token.get('screen_name'), session)
    user.save()
    redirect('/home')
    
@route('/logout')
def logout():
    response.delete_cookie('t')
    redirect('/')
    

bottle.debug(True)
run(host='0.0.0.0', port=8080, reloader=True)