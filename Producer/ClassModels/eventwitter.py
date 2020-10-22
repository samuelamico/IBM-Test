from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import json
import logging
import asyncio
from confluent_kafka import Producer
from .tweet import Tweet
from geopy.geocoders import Nominatim
from time import sleep,time
"""
Classe contida neste arquivo deve realizar a função de coletar os eventos gerados pelo Twitter,
e produzir para um topico Kafka Hub. Sera aplicado as seguintes operações:
    * Extract: Extração dos eventos Twitter.
    * Transform: A operacao de transformacao aplicada será apenas filtrar campos do evento relevantes.
    * Load: Carregar para o Kafka os eventos.

Regras de Escalabildiade para obedecer:
    * O codigo deve ser encapsulado em container , no minimo 3 para garantir um quorom base minimo.
    * O codigo pode ser escalavel utilizando o Zookeeper em uma arquitetura MultiMaquinas com pequenos Nodes.
    * Garantir Resiliencia armazenando no Kafka com no minimo 3 brokers geograficamente distantes, Garantir Mantenabilidade capturando Logs para Monitorar


A classe e herdada pela super classe StreamListener feita na biblioteca tweepy. Para manter uma estrutura escalava e imutavel que deve ser presente
em uma arquitetura de unbounded data, funcoes como Map e Filter sao ideais. A linguagem de programacao Scala e uma alternativa viavel.
"""

### Kafka Configs ---> File or LOCALENV.

logger = logging.getLogger(__name__)

class Eventwitter(StreamListener):
    def __init__(self, name,time_limit=100):
        super().__init__(self)
        self.name = name
        self.locator = Nominatim(user_agent="myGeocoder")
        self.start_time = time()
        self.limit = time_limit

        # Kafka config
        self.broker = "localhost:9092"
        self.topic_name = "eventcrud.twitter.json"

        self.producer =  Producer({   
            "bootstrap.servers":"localhost:9092" ,
            "client.id": "tweet",
            "batch.num.messages": "100",
        })

    def location_nominatuim(self,address):
        try:
            location = self.locator.geocode('Brazil - '+ event.user.location)
            return(location.latitude,location.longitude)
        except:
            return(None,None)
            logger.info("Cannot Convert the Specifed Location to Lat,Lon")

    def on_data(self, data):
        # Para melhor aproveitamento de largura de banda devera ser enviado para o Kafka Na forma de Avro
        if (time() - self.start_time) < self.limit:
            event = json.loads(data)
            lat,lon = self.location_nominatuim(event['user']['location'])
            event_tweet = Tweet(event['created_at'],event['id'],event['text'],event['user']['id'],event['user']['name'],event['user']['location'],event['user']['created_at'],lat,lon)

            self.producer.produce(
                self.topic_name,
                json.dumps({"event_time":event_tweet.event_created_at,"event_id":event_tweet.event_id,"text":event_tweet.text,"user_id":event_tweet.user_id,"user_name":event_tweet.user_name,
                "location":event_tweet.user_location,"twitter_create_at":event_tweet.tweet_created_at})
            )
            return True
        else:
            return False
        
        


    def on_error(self, status):
        # Para um melhor funcionamento devera ser tratado as excecoes -->
        logging.error(status)