import re

import httplib2
from lxml import etree
import twitter
from pymongo import Connection
from twittergrafico.agrupacion import Clustering
from twittergrafico.seleccion import Seleccion

class Twitter_Dal(object):
    
    # I have to include the Mongo config
    
    def __init__(self, id, user, message, host = 'localhost', database = 'twitter_grafico'):
        self.id = id
        self.user = user
        self.message = message
        self.url = self.get_url(message)
        connection = Connection(host = host)
        result = connection[database].tweets.find_one({"id":id})
        self.image = None
        self.keywords = None
        if result:
            self.image = result.get('image')
            self.title = result.get('title')
            self.description = result.get('description')
        else:
            if self.url:
                params = self.get_representative_image_keywords(self.url)
                self.image = params.get('image')
                self.keywords = params.get('keywords')
            self.save(host = host, database = database)
        connection.disconnect()
    
    '''def __init__(self, id, user, message, image, url):
        self.id = id
        self.user = user
        self.message = message
        self.image = image
        self.url = url
    
    @staticmethod
    def get_twitter_messages(user, limit):
        host = 'localhost'
        database = 'twitter_grafico'
        connection = Connection(host = host)
        results = connection[database].tweets.find(limit=limit)
        tweet_objects = []
        for result in results:
            tweet_objects.append(Twitter_Dal(result.get('id'), result.get('user'), result.get('message'), result.get('image'), result.get('url')))
        # should return Twitter_Dal objects
        return tweet_objects'''
    
    @staticmethod
    def get_twitter_messages(user, limit):
        # Have to fix this so it takes data from OAuth
        api = twitter.Api(consumer_key='H8XJeW1h6f8pdFcdWqlA', consumer_secret='N0FIYX4jHZzovkpVLTjSrf3M7kf0PdyHHgW1r0xQ6o', access_token_key='307955415-yPEtTvE5Tzf9gJZCdmwQYGEQFFhoWDim1pZq7olD', access_token_secret='U4YVdwsJQCPtSM5vix5Q85q2PRLpZBK2enwMFFiI1o')
        tweets = api.GetFriendsTimeline(user=user, count=limit, include_entities=True)
        tweet_objects = []
        for tweet in tweets:
            tweet_objects.append(Twitter_Dal(tweet.id, tweet.user.id, tweet.text))
        # should return Twitter_Dal objects
        return tweet_objects

    def save(self, host = 'localhost', database = 'twitter_grafico'):
        connection = Connection(host = host)
        result = connection[database].tweets.find_one({"id":self.id})
        if result:
            connection[database].tweets.save(self.__dict__.append({"_id": result.get("_id")}))
        else:
            connection[database].tweets.save(self.__dict__)
        connection.disconnect()
    
    @staticmethod
    def get_url(message):
        url = re.search("((https?|ftp|gopher|telnet|file|notes|ms-help):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", message)
        if url:
            return url.group(0)
        return None
    
    @staticmethod
    def get_representative_image_keywords(url):
        # Returns the image and info if the image exists, otherwise returns None
        http = httplib2.Http()
        headers, content = http.request(url)
        parser = etree.HTMLParser()
        tree = etree.fromstring(content, parser)
        image_url = tree.xpath('.//meta[@property="og:image"]/@content')
        keywords = tree.xpath('.//meta[@name="keywords"]/@content')
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
        # The title and the description have information about the site, not about the news, so it's not useful
        return {'image': image_url, 'keywords': keywords }
    

if __name__ == "__main__":
    # This should be out of here.  
    messages = Twitter_Dal.get_twitter_messages('jivasquez0', 10)
    for message in messages:
            pass
    clustering = Clustering(messages, 'jivasquez0')
    clusters = clustering.clusters
    print clusters
    filename = clustering.filename+'.info'
    seleccion = Seleccion(clusters, filename)
    print seleccion.representative_tweets