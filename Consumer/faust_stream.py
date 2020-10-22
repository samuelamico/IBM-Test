import logging
import faust
import pickle
import re
import nltk
from nltk.tokenize import word_tokenize
from string import punctuation 
from nltk.corpus import stopwords 
import pandas as pd
import configparser
from elastic_core import ElasticSend

global es
es = ElasticSend()

### Import the classifier and word extraction
def word():
    def buildVocabulary(preprocessedTrainingData):
        all_words = []
        
        for (words, sentiment) in preprocessedTrainingData:
            all_words.extend(words)

        wordlist = nltk.FreqDist(all_words)
        word_features = wordlist.keys()
        
        return word_features

    def processTweetBayes(tweet):
        tweet = tweet.lower()
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
        tweet = re.sub('@[^\s]+', 'AT_USER', tweet) 
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet) 
        stopwords = set(nltk.corpus.stopwords.words('portuguese'))
        palavras = [word for word in tweet.split() if word not in stopwords]
        return (palavras)


    def createProcessTweets(df):
        processdTweet = []
        for index,row in df.iterrows():
            processdTweet.append((processTweetBayes(row[2]),row[9]))
        return processdTweet

    dataset = pd.read_csv('ML/Data/Tweets_Mg.csv', encoding='utf-8')
    trainingSet =  createProcessTweets(dataset)
    word_features = buildVocabulary(trainingSet)
    return(word_features)

f = open('BayesClassify.pickle', 'rb')
global classifier
classifier = pickle.load(f)
f.close()

global word_features
word_features = word()




logger = logging.getLogger(__name__)


###### Text Extraction:
def PreprocessingNewTweet(tweet):

    def processTweetBayes(tweet):
        tweet = tweet.lower()
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
        tweet = re.sub('@[^\s]+', 'AT_USER', tweet) 
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet) 
        stopwords = set(nltk.corpus.stopwords.words('portuguese'))
        palavras = [word for word in tweet.split() if word not in stopwords]
        return (palavras)

    return processTweetBayes(tweet)


def extract_features(tweet):
    tweet_words = set(tweet)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in tweet_words)
    return features 

def SentimentalAlgorithm(tweet_text):
    processdtweet = PreprocessingNewTweet(tweet_text)
    NBResultLabels = classifier.classify(extract_features(processdtweet))
    return(NBResultLabels)

##### End of ML extraction


# Faust vai ingerir os eventos vindos do Kafka neste formato:
class Tweeters(faust.Record):
    event_time: str
    event_id: int
    text: str
    user_id: int
    user_name: str
    location: str
    twitter_create_at: str

# Faust vai produzir eventos nesse formato
class TweeterLabeled(faust.Record):
    event_created_at: str
    event_id: int
    text: str
    user_id: int
    user_name: str
    location: str
    sentimental: str


app = faust.App(
    'StreamingML',
    broker='kafka://localhost:9092',
)

twetts_topic = app.topic('eventcrud.twitter.json',value_type=Tweeters)



### Streaming Service
# Start: faust -A faust_stream worker -l info

config = configparser.ConfigParser()

config.read('load.ini')
bulk_size = config['bulk']['size']
index_elastic = str(config['bulk']['indice'])

import datetime
@app.agent(twetts_topic)
async def tweetvent(tweets):
    async for tweet in tweets:
        ### ML Class:
        tweetlabeled = {
            "event_created_at": datetime.datetime.strptime(tweet.event_time, '%a %b %d %H:%M:%S %z %Y').strftime("%Y-%m-%d %H:%M:%S"),
            "event_id": tweet.event_id,
            "text": tweet.text,
            "text_keyword": tweet.text,
            "user_id": tweet.user_id,
            "user_name": tweet.user_name,
            "location": tweet.location,
            "twitter_create_at": datetime.datetime.strptime(tweet.twitter_create_at, '%a %b %d %H:%M:%S %z %Y').strftime("%Y-%m-%d %H:%M:%S"),
            "sentimental": SentimentalAlgorithm(tweet.text)         
        }
        ## Send to ElasticSearch Cloud - Streaming Load
        es.send_to_elastic(tweetlabeled,index_elastic)



