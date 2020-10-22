from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
from confluent_kafka.admin import AdminClient, NewTopic
import asyncio
from confluent_kafka import Consumer, Producer
from dataclasses import asdict, dataclass, field
import asyncio
import configparser
import json
import random
import sys
from ClassModels.eventwitter import Eventwitter


### Logging Configuration:



def config_api():
    config = configparser.ConfigParser()

    config.read('config.ini')
    consumer_key = config['auth']['consumer_key']
    consumer_secret = config['auth']['consumer_secret']
    access_token = config['auth']['access_token']
    access_token_secret = config['auth']['access_token_secret']

    return(consumer_key,consumer_secret,access_token,access_token_secret)


async def stream(track: list):
    '''
    Conecta a API do Twitter e retorna os tweets que estão sendo postados na plataforma em tempo real.
    Essa função é executada durante 10 minutos e depois desconecta o stream.
    Para executá-la é necessário que o arquivo config.ini esteja preenchido com os dados de acesso à API do Twitter.
    '''
    consumer_key,consumer_secret,access_token,access_token_secret = config_api()
    print(f"Iniciando stream para track:{track}")
    await asyncio.sleep(random.randint(10, 20))
    
    assinante = Eventwitter(track)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Iniciando Streaming event:
    stream = Stream(auth=auth, listener=assinante, tweet_mode='extended')
    # Executando Stream com filtro

    stream.filter(track=track, is_async=True, languages=["pt"])
    await asyncio.sleep(120) # Run for 1 minute

    stream.disconnect()


async def main():
    '''
    Exectuar "Threads" para topicos diferentes
    '''
    await asyncio.gather(
        stream(['governo']),
        stream(['covid']),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("shutting down")