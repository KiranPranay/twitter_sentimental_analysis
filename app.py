import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
from flask import Flask, render_template, redirect, url_for, request

# Clean tweet by removing unnecessary characters
def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

# Get sentiment of tweet
def get_tweet_sentiment(tweet):
    analysis = TextBlob(clean_tweet(tweet))
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return 'positive'
    elif polarity == 0:
        return 'neutral'
    else:
        return 'negative'

# Get tweets from Twitter API and assign sentiment
def get_tweets(api, query, count=5):
    count = int(count)
    try: 
        fetched_tweets = tweepy.Cursor(api.search, q=query, lang='en', tweet_mode='extended').items(count)
        tweets = []
        for tweet in fetched_tweets:
            parsed_tweet = {}
            if 'retweeted_status' in dir(tweet):
                parsed_tweet['text'] = tweet.retweeted_status.full_text
            else:
                parsed_tweet['text'] = tweet.full_text
            parsed_tweet['sentiment'] = get_tweet_sentiment(parsed_tweet['text'])
            if tweet.retweet_count > 0:
                if parsed_tweet not in tweets:
                    tweets.append(parsed_tweet)
            else:
                tweets.append(parsed_tweet)
        return tweets
    except tweepy.TweepError as e:
        print(f"Error: {e}")

app = Flask(__name__)

# Twitter API authentication
consumer_key = 'your_consumer_key'
consumer_secret = 'your_consumer_secret'
access_token = 'your_access_token'
access_token_secret = 'your_access_token_secret'

try: 
    auth = OAuthHandler(consumer_key, consumer_secret)  
    auth.set_access_token(access_token, access_token_secret) 
    api = tweepy.API(auth)
except: 
    print("Error: Authentication Failed") 

@app.route('/')
@app.route('/index')
def home():
    return render_template('index.html')

# new route to about.html
@app.route('/about')
def about():
    return render_template('about.html')


# Phrase level sentiment analysis
@app.route("/predict", methods=['POST','GET'])
def pred():
    if request.method=='POST':
            query=request.form['query']
            count=request.form['num']
            fetched_tweets = get_tweets(api,query, count) 
            return render_template('result.html', result=fetched_tweets)

# Sentence level sentiment analysis
@app.route("/predict1", methods=['POST','GET'])
def pred1():
    if request.method=='POST':
            text = request.form['txt']
            blob = TextBlob(text)
            if blob.sentiment.polarity > 0:
                text_sentiment = "Positive"
            elif blob.sentiment.polarity == 0:
                text_sentiment = "Neutral"
            else:
                text_sentiment = "Negative"
            return render_template('result1.html',msg=text, result=text_sentiment)

if __name__ == '__main__':
    app.run(debug=True)