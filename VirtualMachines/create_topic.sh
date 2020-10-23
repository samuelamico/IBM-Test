#!/bin/bash

name=$1

echo "Creating a Topic: $name"
echo "-- Topic uses clean.up = delete,"
echo "-- replication of 2, using json schema"

echo ``` /usr/local/kafka/bin/kafka-topics.sh --create --topic $name --config cleanup.policy=delete --partitions 2 --replication-factor 1 --zookeeper localhost:2181 ```
echo " ------- TOPIC $name CREATE -------"

name2=$2

echo "Creating a Topic: $name2"
echo "-- Topic uses clean.up = compact,lz4"
echo "-- replication of 2, using avro schema"

echo ``` /usr/local/kafka/bin/kafka-topics.sh --create --topic $name2  --partitions 2 --replication-factor 1  --zookeeper localhost:2181 ```
echo " ------- TOPIC $name2 CREATE -------"
