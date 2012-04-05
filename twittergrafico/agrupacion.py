# -*- coding: utf-8 -*-
import os
import unicodedata
import string

class Clustering():
    
    def __init__(self, tweets, user, text_source='message', rowmodel='none', clmethod='rb'):
        #tweets is a list of Twitter_Dal objects
        self.tweets = tweets
        self.user = user.screen_name
        self.filename = self.generate_documents_file(text_source)
        self.generate_mat_file(self.filename)
        cluster_number = int(len(tweets)/4)
        self.cluster_filename = self.generate_cluster_file(self.filename, cluster_number, rowmodel, clmethod)
        self.clusters = self.generate_clusters(self.cluster_filename, cluster_number)
    
    def generate_documents_file(self, text_source='message'):
        #I should use a hash instead
        filename = '/tmp/'+self.user
        file = open(filename, 'w')
        for tweet in self.tweets:
            text = tweet.message
            if text_source=='keywords' and tweet.keywords:
                text = tweet.keywords
            if text_source =='text' and tweet.text:
                text = tweet.text
            #for now we use just the message
            file.write(unicode(Clustering.clean_text(text, tweet.url)+'\n').encode("utf-8"))
        file.close()
        self.filename = filename
        return filename
    
    
    @staticmethod
    def clean_text(text, url=None):
        stopwords = []
        text_array = []
        if url:
            text = text.replace(url, "")
        text = Clustering.remove_user_tags(text)
        text = text.lower()
        for word in Clustering.get_stopwords():
            stopwords.append(Clustering.elimina_tildes(word))
        clean_text = Clustering.elimina_tildes(text)
        for word in clean_text.split():
            if word not in stopwords:
                text_array.append(word)
        return string.join(text_array)
    
    @staticmethod
    def elimina_tildes(text):
        #elimina tildes y puntuación en general
        if type(text) == str:
            text = unicode(text, "utf-8")
        texto = ''.join((c for c in unicodedata.normalize('NFD', text ) if unicodedata.category(c) != 'Mn'))
        for char in string.punctuation:
            texto = texto.replace(char, "")
        return texto
    
    @staticmethod
    def remove_user_tags(text):
        clean_text_array = []
        for word in text.split():
            if not word.startswith("@"):
                clean_text_array.append(word)
        return string.join(clean_text_array)
    
    @staticmethod
    def get_stopwords():
        file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stopwords.txt"), 'r')
        stopwords = file.readline()
        return stopwords.split()
        
    @staticmethod
    def generate_mat_file(filename):
        os.system('doc2mat '+filename+' '+filename+'.mat')

    @staticmethod        
    def generate_cluster_file(filename, cluster_number, rowmodel='none', clmethod='rb'):
        os.system('vcluster -showfeatures -clmethod='+ clmethod +' -rowmodel='+ rowmodel + ' '+filename+'.mat '+str(cluster_number)+' > ' + filename + '.info')
        #returns cluster output filename
        return filename+'.mat.clustering.'+str(cluster_number)
        
    def generate_clusters(self, filename, cluster_number):
        clusters = [[] for x in range(0, cluster_number)]
        file = open(filename, 'r')
        for tweet in self.tweets:
            cluster = int(file.readline())
            clusters[cluster].append(tweet)
        return clusters
    