#encoding: utf-8
import asyncio
import json
from confluent_kafka import Consumer, Producer
from time import sleep

BROKER_URL = "PLAINTEXT://localhost:9092"
TOPIC_NAME = "eventcrud.twitter.json"

json_docs = []
global counter_file
counter_file = 0

def save_to_json(counter_file):
    name_file = 'dataset' + str(counter_file) + '.json'
    counter_file = 0
    print("Saving tweets")
    with open(name_file, 'w', encoding='utf8') as json_file:
        json.dump(json_docs, json_file, ensure_ascii=False)

async def consume():
    """Consumes data from the Kafka Topic"""
    counter_file = 0
    c = Consumer({"bootstrap.servers": BROKER_URL, "group.id": "0","auto.offset.reset":"earliest"})
    c.subscribe([TOPIC_NAME])
    while True:
        message = c.poll(1.0)
        if message is None:
            print("no message received by consumer")
        elif message.error() is not None:
            print(f"error from consumer {message.error()}")
        else:
            my_json = (message.value()).decode('utf8').replace("'", '"')
            json_docs.append(my_json)
            print(f"consumed message {message.value()}")
            counter_file+=1
            if(counter_file%30 == 0):
                save_to_json(counter_file)
        await asyncio.sleep(2.5)


def main():
    try:
        asyncio.run(consume())
    except KeyboardInterrupt as e:

        print("shutting down")
        
if __name__ == "__main__":
    main()