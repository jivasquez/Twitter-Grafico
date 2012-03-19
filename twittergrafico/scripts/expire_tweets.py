
from datetime import datetime, timedelta

from twittergrafico.tweets import Twitter_DAO

if __name__ == '__main__':
    today = datetime.utcnow()
    delta = timedelta(days = 1)
    date = today - delta
    Twitter_DAO.expire_tweets_before_date(date)
    