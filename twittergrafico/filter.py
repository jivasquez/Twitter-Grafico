import twittergrafico

class Filter(object):
    def __init__():
        pass
    
    @staticmethod
    def image_filter(tweet):
        #returns true if the filter pass
        if tweet.image and tweet.image not in twittergrafico.FILTERED_IMAGES:
            return True
        return False