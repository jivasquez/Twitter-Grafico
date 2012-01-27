import os

class Clustering():
    
    def __init__(self, tweets, user, text_source='message'):
        #tweets is a list of Twitter_Dal objects
        self.tweets = tweets
        self.user = user
        self.filename = self.generate_documents_file(text_source)
        self.generate_mat_file(self.filename)
        cluster_number = int(len(tweets)/4)
        self.cluster_filename = self.generate_cluster_file(self.filename, cluster_number)
        self.clusters = self.generate_clusters(self.cluster_filename, cluster_number)
    
    def generate_documents_file(self, text_source='message'):
        #I should use a hash instead
        filename = '/tmp/'+self.user
        file = open(filename, 'w')
        for tweet in self.tweets:
            text = tweet.message
            if text_source=='keywords' and tweet.keywords:
                text = tweet.keywords
                print text
            #for now we use just the message
            file.write(unicode(text+'\n').encode("utf-8"))
        file.close()
        self.filename = filename
        return filename
        
    @staticmethod
    def generate_mat_file(filename):
        os.system('doc2mat '+filename+' '+filename+'.mat')

    @staticmethod        
    def generate_cluster_file(filename, cluster_number):
        os.system('vcluster -showfeatures '+filename+'.mat '+str(cluster_number)+' > ' + filename + '.info')
        #returns cluster output filename
        return filename+'.mat.clustering.'+str(cluster_number)
        
    def generate_clusters(self, filename, cluster_number):
        clusters = [[] for x in range(0, cluster_number)]
        file = open(filename, 'r')
        for tweet in self.tweets:
            cluster = int(file.readline())
            clusters[cluster].append(tweet)
        return clusters
    