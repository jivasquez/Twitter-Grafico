# -*- coding: utf-8 -*-
import re
from twittergrafico.filter import Filter

class Seleccion():
    
    def __init__(self, clusters, filename):
        self.clusters = clusters
        self.filename = filename
        cluster_words_percentages = Seleccion.parse_cluster_info(filename)
        self.representative_tweets = Seleccion.obtain_representative_tweets(clusters, cluster_words_percentages)
        
    @staticmethod
    def obtain_representative_tweets(clusters, cluster_words_percentages):
        representative_tweets = {}
        for i in range(0, len(clusters)):
            representative_tweets[i] = Seleccion.get_representative_tweet(clusters[i], cluster_words_percentages[str(i)])
        return representative_tweets
            
        
    @staticmethod
    def parse_cluster_info(filename):
        #Fix clusters_words to be of fixed size
        clusters_words = {}
        file_ = open(filename, 'r')
        line = 'a'
        while line:
            line = file_.readline()
            if line.startswith('Cluster'):
                cluster_number = Seleccion.get_cluster_number(line)
                line = file_.readline()
                info = line.split(':')[1] or ''
                words_percentages = info.split(',')
                words_percentages = map(lambda x: x.strip(), words_percentages)
                words_percentages = map(lambda x: {'word':x.replace('  ',' ').split(' ')[0], 'percentage': x.replace('  ',' ').split(' ')[1].rstrip('%')}, words_percentages)
                clusters_words[cluster_number] = words_percentages
        return clusters_words
    
    @staticmethod
    def get_representative_tweet(cluster, scores):
        if not cluster:
            return None
        tweet_scores = {}
        for tweet in cluster:
            if tweet.image:
                tweet_scores[tweet.id] = 10
            else:
                tweet_scores[tweet.id] = 0
        for word in scores:
            for tweet in cluster:
                #check if word exists on the tweet
                if tweet.message.find(word.get('word')) != -1 and Filter.image_filter(tweet):
                    tweet_scores[tweet.id] = tweet_scores.get(tweet.id, 0) + float(word.get('percentage'))*100
        normalized_scores = Seleccion.normalize(tweet_scores, cluster)
        best_score = (normalized_scores.keys()[0], -1)
        for tweet_id, score in normalized_scores.iteritems():
            if score > best_score[1]:
                best_score = (tweet_id, score)
        for tweet in cluster:
            if tweet.id == best_score[0]:
                return tweet
        return None
        
    @staticmethod
    def normalize(tweet_scores, cluster):
        normalized_scores = {}
        for tweet in cluster:
            count = len(tweet.message.split(" "))
            normalized_scores[tweet.id] = tweet_scores.get(tweet.id, 0)/count
        return normalized_scores
                
    @staticmethod
    def get_cluster_number(line):
        result = re.search(r"Cluster( +)(?P<number>[0-9]+)", line)
        return result.group('number')