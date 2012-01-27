import os

from bottle import route, run, static_file
import bottle
from bottle import mako_view as view, mako_template as template

from twittergrafico.agrupacion import Clustering
from twittergrafico.seleccion import Seleccion
from twittergrafico.tweets import Twitter_Dal
from twittergrafico.filter import Filter


@route('/clustered_tweets')
def clustered():
    messages = Twitter_Dal.get_twitter_messages('jivasquez0', 50)
    clustering = Clustering(messages, 'jivasquez0')
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return template('templates/clustered_list.html', clusters=clusters, representative=seleccion.representative_tweets, messages=messages)
    
@route('/static/<path:path>')
def static(path):
    ASSETS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    return static_file(path, ASSETS_PATH)

@route('/home')
def home():
    return template('templates/home.html', asd='asd')
    
@route('/list')
def list():
    messages = Twitter_Dal.get_twitter_messages('jivasquez0', 50)
    filtered_messages = []
    for index, message in enumerate(messages):
        if  Filter.image_filter(message):
            filtered_messages.append(messages[index])
    return template('templates/list.html', messages=filtered_messages)
    
@route('/clustered_keywords')
def keywords():
    messages = Twitter_Dal.get_twitter_messages('jivasquez0', 50)
    clustering = Clustering(messages, 'jivasquez0', 'keywords')
    clusters = clustering.clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    return template('templates/clustered_list.html', clusters=clusters, representative=seleccion.representative_tweets, messages=messages)
    
    
    
    
    @bottle.route('/api/login_url', method = 'GET')    
def get_login_url():
    auth = tweepy.OAuthHandler(
        os.environ['FCLIENTS_CONSUMER_KEY'],
        os.environ['FCLIENTS_CONSUMER_SECRET'],
        TWITTER_CALLBACK
    )
    redirect_url = auth.get_authorization_url()
    request_key = auth.request_token.key
    request_secret = auth.request_token.secret

    id_token = sha1(request_key+request_secret).hexdigest()
    request.db.users.insert({'request_key': request_key, 'request_secret': request_secret, 'sha1': id_token , 'date_create': datetime.utcnow()})
    response.set_cookie("t", id_token, path='/')
    return [redirect_url,]


'''@bottle.route('/api/login', method = 'GET')    
def login():
    auth = tweepy.OAuthHandler(
        os.environ['FCLIENTS_CONSUMER_KEY'],
        os.environ['FCLIENTS_CONSUMER_SECRET'],
        TWITTER_CALLBACK
    )

    oauth_token = request.GET.get('oauth_token')
    oauth_verifier = request.GET.get('oauth_verifier')

    token = request.db.users.find_one({'sha1': request.get_cookie("t")})
    if token:
        auth.set_request_token(token.get('request_key'), token.get('request_secret'))
        auth.get_access_token(oauth_verifier)
        access_key = auth.access_token.key
        access_secret = auth.access_token.secret

        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)
        user = api.me()

        request.db.users.update(
            {'sha1': request.get_cookie("t")},
            {'$set': {'access_key': access_key, 'access_secret': access_secret, 'screen_name': user.screen_name, 'twitter_id': user.id, 'name': user.name}}
        )
        bottle.redirect('/clients.html')
    bottle.redirect('/index.html')







#UTILIZAR CUENTA

auth = tweepy.OAuthHandler(
    os.environ['FCLIENTS_CONSUMER_KEY'],
    os.environ['FCLIENTS_CONSUMER_SECRET']
)
auth.set_access_token(user.get('access_key'), user.get('access_secret'))
api = tweepy.API(auth)
api.update_status(final_message)
'''
    

bottle.debug(True)
run(host='localhost', port=8080, reloader=True)