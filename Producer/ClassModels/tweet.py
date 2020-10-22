import logging
from pathlib import Path
from confluent_kafka import avro
from confluent_kafka import  Producer
import json
import time

logger = logging.getLogger(__name__)


class Tweet():
    """Defines a single Tweet Event"""
    #value_schema = avro.load(f"{Path(__file__).parents[0]}/schemas/tweets.json")

    def __init__(self,event_created_at,event_id,text,user_id,user_name,user_location,tweet_created_at,lat,lon):
        self.event_created_at = event_created_at
        self.event_id = event_id
        self.text = text
        self.user_id = user_id
        self.user_name = user_name
        self.user_location = user_location
        self.tweet_created_at = tweet_created_at
        self.lat = lat
        self.lon = lon

        # Kafka config
        self.broker = "localhost:9092"
        self.topic_name = "eventcrud.twitter.json"
        self.p = Producer({   
            "bootstrap.servers":self.broker ,
            "client.id": "tweet",
            "batch.num.messages": "100",
        })

    def __str__(self):
        return (f'Event Time = {self.event_created_at} , Event_id = {self.event_id} , Text = {self.text}, User = {self.user_id,self.user_name}, Location = {self.user_location,self.lat,self.lon}')

    def serialize(self):
        return json.dumps(
            {"event_time":self.event_created_at,"event_id":self.event_id,"text":self.text,"user_id":self.user_id,"user_name":self.user_name,
            "location":self.user_location}
        )



