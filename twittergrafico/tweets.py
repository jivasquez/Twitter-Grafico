import re

import httplib2
from lxml import etree
import twitter
from pymongo import Connection

class Twitter_Dal(object):
    
    # I have to include the Mongo config
    
    def __init__(self, id, user, message, host = 'localhost', database = 'twitter_grafico'):
        self.id = id
        self.user = user
        self.message = message
        self.url = get_url(message)
        connection = Connection(host = host)
        result = connection[database].tweets.find_one({"id":id})
        self.image = None
        self.title = None
        self.description = None
        if result:
            self.image = result.get('image')
            self.title = result.get('title')
            self.description = result.get('description')
        else:
            params = get_representative_image_title_description(self.url)
            self.image = params.get('image')
            self.title = params.get('title')
            self.description = params.get('description')
            self.save(host = host, database = database)
        connection.disconnect()
        

    def get_twitter_messages(user, limit):
        # Have to fix this so it takes data from OAuth
        api = twitter.Api(consumer_key='H8XJeW1h6f8pdFcdWqlA', consumer_secret='N0FIYX4jHZzovkpVLTjSrf3M7kf0PdyHHgW1r0xQ6o', access_token_key='307955415-yPEtTvE5Tzf9gJZCdmwQYGEQFFhoWDim1pZq7olD', access_token_secret='U4YVdwsJQCPtSM5vix5Q85q2PRLpZBK2enwMFFiI1o')
        tweets = api.GetFriendsTimeline(user=user, count=limit, include_entities=True)
        # should return Twitter_Dal objects
        return tweets

    def save(self, host = 'localhost', database = 'twitter_grafico'):
        connection = Connection(host = host)
        result = connection[database].tweets.find_one({"id":self.id}):
        if result:
            connection.[database].tweets.save(self.__dict__.append({"_id": result.get("_id")}))
        else:
            connection.[database].tweets.save(self.__dict__)
        connection.disconnect()
    
    @staticmethod
    def get_url(message):
        url = re.search("((https?|ftp|gopher|telnet|file|notes|ms-help):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", message)
        if url:
            return url.group(0)
        return None
    
    @staticmethod
    def get_representative_image_title_description(url):
        # Returns the image and info if the image exists, otherwise returns None
        http = httplib2.Http()
        headers, content = http.request(url)
        parser = etree.HTMLParser()
        tree = etree.fromstring(content, parser)
        image_url = tree.xpath('.//meta[@property="og:image"]/@content')
        if len(image_url) == 0:
            image_url = tree.xpath('.//link[@rel="image_src"]/@href')
        if len(image_url) == 0:
            return None
        # Have to parse the rest of the info
        return {'image': image_url[0], 'title': None, 'description': None }
    
    # This should be out of here.  
messages = get_twitter_messages('jivasquez0', 10)
print messages