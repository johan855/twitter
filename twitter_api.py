#Python3

import re
import tweepy
from datetime import datetime, timedelta
from nltk.tokenize import WordPunctTokenizer
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from twitter_api_credentials import TwitterCredentials


def authenticate():
    KEY = TwitterCredentials.KEY
    KEY_SECRET = TwitterCredentials.KEY_SECRET
    TOKEN = TwitterCredentials.TOKEN
    TOKEN_SECRET = TwitterCredentials.TOKEN_SECRET
    auth = tweepy.OAuthHandler(KEY, KEY_SECRET)
    auth.set_access_token(TOKEN, TOKEN_SECRET)
    api = tweepy.API(auth)
    return api


def get_user_id(api, user_name):
    user = api.get_user(user_name)
    user_id = user.id
    return user_id


def search_tweets(search_date, total_tweets, user_name, api):
    user_id = get_user_id(api, user_name)
    search_result = tweepy.Cursor(api.user_timeline,
                                  since=search_date,
                                  id=user_id,
                                  lang='en').items(total_tweets)
    return search_result


def clean_tweets(tweet):
    tweet_users = re.findall(r'@[A-Za-z0-9]+',tweet.decode('utf-8'))
    user_removed = re.sub(r'@[A-Za-z0-9]+','',tweet.decode('utf-8'))
    tweet_links = re.findall('https?://[A-Za-z0-9./]+',user_removed)
    link_removed = re.sub('https?://[A-Za-z0-9./]+','',user_removed)
    number_removed = re.sub('[^a-zA-Z]', ' ', link_removed)
    lower_case_tweet= number_removed.lower()
    tok = WordPunctTokenizer()
    words = tok.tokenize(lower_case_tweet)
    clean_tweet = (' '.join(words)).strip()
    return clean_tweet, tweet_users, tweet_links


def get_sentiment_score(tweet):
    client = language.LanguageServiceClient()
    document = types.Document(content=tweet,type=enums.Document.Type.PLAIN_TEXT)
    sentiment_score = client.analyze_sentiment(document=document).document_sentiment.score
    sentiment_magnitude = client.analyze_sentiment(document=document).document_sentiment.magnitude
    return sentiment_score, sentiment_magnitude


def tweet_sentiment_analysis(total_tweets, yesterday_date, user_name):
    score = 0
    api = authenticate()
    tweets = search_tweets(yesterday_date, total_tweets, user_name, api) #Download tweets
    for tweet in tweets:
        cleaned_tweet, tweet_users, tweet_links = clean_tweets(tweet.text.encode('utf-8'))
        sentiment_score, sentiment_magnitude = get_sentiment_score(cleaned_tweet)
        score += sentiment_score
        print('Tweet: {0}'.format(cleaned_tweet))
        print('Users: {0}'.format(tweet_users))
        print('Links: {0}'.format(tweet_links))
        print('Score: {0}'.format(sentiment_score))
        print('Magnitude: {0}\n'.format(sentiment_magnitude))
    final_score = round((score / float(total_tweets)),2)
    return final_score, tweets


def update_status(api):
    api.update_status('test status')


if __name__=='__main__':
    keyword = ''
    total_tweets = 20
    user_name = 'round_boys'
    today_date = datetime.now()
    yesterday = today_date - timedelta(days=1)
    yesterday_date = yesterday.strftime('%Y-%m-%d')
    tweet_sentiment_analysis(total_tweets, yesterday_date, user_name)