# -*- coding: utf-8 -*-
import re
from datetime import datetime

import httplib2
from lxml import etree
import twitter
from pymongo import Connection

from twittergrafico.agrupacion import Clustering
from twittergrafico.seleccion import Seleccion
from twittergrafico.user import User

MASSIVE_USER_FOLLOWERS = 3000

class Twitter_DAO(object):
    
    # I have to include the Mongo config
    
    def __init__(self, tweet, host = 'localhost', database = 'twitter_grafico', displayed = False):
        
        self.id = tweet.id
        self.user = tweet.user.id
        self.message = tweet.text
        #The date comes in GTM
        self.created_at = datetime.strptime(tweet.created_at,"%a %b %d %H:%M:%S +0000 %Y")
        self.url = self.get_url(self.message)
        User(tweet.user.id, tweet.user.screen_name, tweet.user.followers_count).save()
        connection = Connection(host = host)
        result = connection[database].tweets.find_one({"id":self.id})
        self.image = None
        self.keywords = None
        self.text = None
        self.massive = False
        if displayed:
            self.displayed = True
        self.check_massive_users(tweet.user)
        if result:
            self.image = result.get('image')
            self.text = result.get('text')
        else:
            if self.url:
                params = self.get_representative_image_keywords(self.url)
                self.image = params.get('image')
                self.keywords = params.get('keywords')
                self.text = params.get('text')
            self.save(host = host, database = database)
        connection.disconnect()
    
    '''def __init__(self, id, user, message, image, url):
        self.id = id
        self.user = user
        self.message = message
        self.image = image
        self.url = url
        self.massive = False
        self.text = message
        self.created_at = None'''
    
    '''@staticmethod
    def get_twitter_messages(user, limit):
        host = 'localhost'
        database = 'twitter_grafico'
        connection = Connection(host = host)
        results = connection[database].tweets.find(limit=limit)
        tweet_objects = []
        for result in results:
            tweet_objects.append(Twitter_DAO(result.get('id'), result.get('user'), result.get('message'), result.get('image'), result.get('url')))
        # should return Twitter_DAO objects
        return tweet_objects'''
    
    @staticmethod
    def get_twitter_messages(user, limit):
        # Have to fix this so it takes data from OAuth
        api = twitter.Api(consumer_key='H8XJeW1h6f8pdFcdWqlA', consumer_secret='N0FIYX4jHZzovkpVLTjSrf3M7kf0PdyHHgW1r0xQ6o', access_token_key=user.oauth_token, access_token_secret=user.oauth_token_secret)
        tweets = api.GetFriendsTimeline(user=user.user_id, count=limit, include_entities=True)
        tweet_objects = []
        for tweet in tweets:
            tweet_objects.append(Twitter_DAO(tweet, displayed = True))
        return tweet_objects

    def save(self, host = 'localhost', database = 'twitter_grafico'):
        connection = Connection(host = host)
        result = connection[database].tweets.find_one({"id":self.id})
        if result:
            self._id = result.get("_id")
            connection[database].tweets.update({'_id': result.get("_id")}, self.__dict__)
        else:
            connection[database].tweets.save(self.__dict__)
        connection.disconnect()
    
    @staticmethod
    def get_messages_without_login(user, limit):
        '''Returns tweets without the need of beeing logged in, its used for retreiving tweets with the script from users with many followers'''
        api = twitter.Api()
        tweets = api.GetUserTimeline(user_id=user.user_id, count=limit, include_entities=True)
        tweet_objects = []
        for tweet in tweets:
            tweet_objects.append(Twitter_DAO(tweet))
        return tweet_objects
    
    @staticmethod
    def get_messages_from_search(search):
        api = twitter.Api()
        tweets = api.GetSearch(term=search, per_page=50)
        tweet_objects = []
        for tweet in tweets:
            tweet_objects.append(Twitter_DAO(tweet, displayed = True))
        return tweet_objects
    
    @staticmethod
    def get_url(message):
        url = re.search("((https?|ftp|gopher|telnet|file|notes|ms-help):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", message)
        if url:
            return url.group(0)
        return None
        
    @staticmethod
    def expire_tweets_before_date(date, host = 'localhost', database = 'twitter_grafico'):
        '''expire all the tweets created before the given date
        The date should be a datetime date'''
        connection = Connection(host = host)
        results = connection[database].tweets.remove({"created_at":{"$lt": date}})
    
    @staticmethod
    def get_representative_image_keywords(url):
        # Returns the image and info if the image exists, otherwise returns None
        http = httplib2.Http(timeout=5)
        try:
            headers, content = http.request(url)
            parser = etree.HTMLParser()
            tree = etree.fromstring(content, parser)
            image_url = tree.xpath('.//meta[@property="og:image"]/@content')
            keywords = tree.xpath('.//meta[@name="keywords"]/@content')
            raw_text = tree.xpath('.//p/text()')
            raw_strong = tree.xpath('.//strong/text()')
            text = ''
            for paragraph in raw_text:
                text = text + paragraph
            for words in raw_strong:
                text = text + words
            
            print raw_strong
            if len(image_url) == 0:
                image_url = tree.xpath('.//link[@rel="image_src"]/@href')
            if len(image_url) == 0:
                image_url = None
            else:
                image_url = image_url[0]
            if len(keywords) == 0:
                keywords = None
            else:
                keywords = keywords[0]
        except:
            image_url = None
            keywords = None
            text = None
        # The title and the description have information about the site, not about the news, so it's not useful
        return {'image': image_url, 'keywords': keywords , 'text': text}


    def check_massive_users(self, user):
        if user.followers_count > MASSIVE_USER_FOLLOWERS:
            self.massive = True
    