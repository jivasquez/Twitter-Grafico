
from pymongo import Connection

class Account(object):
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def save(self, host = 'localhost', database = 'twitter_grafico'):
        connection = Connection(host = host)
        result = connection[database].accounts.find_one({"username":self.username})
        if result:
            self.__dict__['username'] = result.get("username")
            connection[database].accounts.update({'username': result.get("username")}, self.__dict__)
        else:
            connection[database].accounts.save(self.__dict__)
        connection.disconnect()
    
    @staticmethod
    def get_user(username, host = 'localhost', database = 'twitter_grafico'):
        connection = Connection(host = host)
        result = connection[database].accounts.find_one({"username":username})
        if result:
            user = Account(result.get('username'), result.get('password'))
            user.__dict__ = result
            return user
        else:
            return None
            
    @staticmethod
    def get_user_from_session_id(session_id, host = 'localhost', database = 'twitter_grafico'):
        connection = Connection(host = host)
        result = connection[database].accounts.find_one({"session":session_id})
        if result:
            user = Account(result.get('username'), result.get('password'))
            user.__dict__ = result
            return user
        else:
            return None
            
    @staticmethod
    def get_user_from_key(key, host = 'localhost', database = 'twitter_grafico'):
        connection = Connection(host = host)
        result = connection[database].accounts.find_one({"key":key})
        if result:
            user = Account(result.get('username'), result.get('password'))
            user.__dict__ = result
            return user
        else:
            return None
