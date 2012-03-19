
from twittergrafico.user import User
from twittergrafico.tweets import Twitter_DAO

FOLLOWERS = 3000

if __name__ == '__main__':
    users = User.find_users_with_many_followers(FOLLOWERS)
    for user in users:
        messages = Twitter_DAO.get_messages_without_login(user=user, limit=10)
        for message in messages:
            print message.__dict__
            message.save()
    