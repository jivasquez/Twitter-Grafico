

from pymongo import Connection

class User(object):
    
    def __init__(self, user_id, username, followers):
        self.user_id = user_id
        self.username = username
        self.followers = followers
        
    def save(self, host = 'localhost', database = 'twitter_grafico'):
        connection = Connection(host = host)
        result = connection[database].users.find_one({"user_id":self.user_id})
        if result:
            connection[database].users.update({'user_id': self.user_id}, self.__dict__)
        else:
            connection[database].users.save(self.__dict__)
        connection.disconnect()
        
    @staticmethod
    def get_user(user_id):
        connection = Connection(host = host)
        result = connection[database].users.find_one({"user_id":self.user_id})
        if result:
            return User(result.get('user_id'), result.get('username'), result.get('followers'))
        else:
            return None
            
    @staticmethod
    def find_users_with_many_followers(followers = 3000):
        connection = Connection(host = host)
        results = connection[database].users.find({"followers": {"$gt": followers}})
        users = []
        for result in results:
            users.append(User(result.get('user_id'), result.get('username'), result.get('followers')))
        return users