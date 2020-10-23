#!/bin/bash

echo "---- STARTING KAFKA BROKER ---"
echo ```sudo /usr/local/zookeeper/bin/zkServer.sh start```

echo "----- STARTING KAFKAR BROKER ----"
echo ```sudo /usr/local/kafka/bin/kafka-server-start.sh -daemon /usr/local/kafka/config/server.properties```
echo "---- BROKER localhost:9092 ------"

echo "----- TOPICS AVAILABE ---------"
echo ```sudo  /usr/local/kafka/bin/kafka-topics.sh --list  --zookeeper localhost:2181```

