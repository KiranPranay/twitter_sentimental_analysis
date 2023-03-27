import re 
import snscrape.modules.twitter as sn
from textblob import TextBlob 
from flask import Flask, render_template, redirect, url_for, request

# Clean tweet by removing unnecessary characters
def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

# Get sentiment of tweet
def get_tweet_sentiment(tweet):
    analysis = TextBlob(clean_tweet(tweet))
    polarity = analysis.sentiment.polarity # type: ignore
    if polarity > 0:
        return 'positive'
    elif polarity == 0:
        return 'neutral'
    else:
        return 'negative'

# Get tweets from Twitter API and assign sentiment
def get_tweets(query, count=5):
    count = int(count)
    tt = sn.TwitterSearchScraper('from:'+query)
    fetched_tweets=[]
    for i, tweeti in enumerate(tt.get_items()):
        if i > count-1:
            break
        fetched_tweets.append(tweeti.rawContent) # type: ignore
    tweets = []
    for tweet in fetched_tweets:
        parsed_tweet = {}
        parsed_tweet['text'] = tweet
        parsed_tweet['sentiment'] = get_tweet_sentiment(parsed_tweet['text'])
        tweets.append(parsed_tweet)
    return tweets

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def home():
    return render_template('index.html')

# new route to sentence.html
@app.route('/sentiment')
def sentence():
    return render_template('sentiment.html')

# new route to about.html
@app.route('/about')
def about():
    return render_template('about.html')

# new route to contact.html
@app.route('/contact')
def contact():
    return render_template('contact.html')


# Phrase level sentiment analysis
@app.route("/predict", methods=['POST','GET']) # type: ignore
def pred():
    if request.method=='POST':
            query=request.form['query']
            count=request.form['num']
            fetched_tweets = get_tweets(query, count)  # type: ignore
            return render_template('result.html', result=fetched_tweets)

# Sentence level sentiment analysis
@app.route("/predict1", methods=['POST','GET']) # type: ignore
def pred1():
    if request.method=='POST':
            text = request.form['txt']
            blob = TextBlob(text)
            if blob.sentiment.polarity > 0: # type: ignore
                text_sentiment = "positive"
            elif blob.sentiment.polarity == 0: # type: ignore
                text_sentiment = "neutral"
            else:
                text_sentiment = "negative"
            return render_template('result1.html',msg=text, result=text_sentiment)

if __name__ == '__main__':
    app.run(debug=True)