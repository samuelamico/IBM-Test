# Twitter - Streaming de Análise Sentimental

O Projeto abaixo trata de resolver o Teste da IBM, onde o objetivo é criar uma arquitetura distribuida, escalável para
analisar os textos - unbounded data - produzidos pelo Twitter (pt-br). O problema em questão se encontra na família de streaming
processing, onde os dados vindos de uma fonte que gera dados infinitos, sem padrão de tempo definido, ou seja unbounded data.

O Processamento de Streaming vem ganhando cada vez mais importancia, pois os metodos de ETL com batch processing engine já não são capazes de suportar a natureza dos dados em streaming. Para isso novas tecnologias e arquiteturas são formuladas para melhor atender a este novo cenario.

O que é Streaming data ?

--- <respodner>

## Pre-requisitos

Os seguintes requisitos são necessários para rodar este projeto:

* Docker
* Python 3.7
* Acesso a um computador de no minimo 16gb+ RAM e 4-core CPU.
* Acesso a um broker Kafka (VM no caso disponibilizada ou então um docker).
* Acesso ao servidor em cloud do ElasticSearch.


## Descrição

O Twitter é uma rede social onde os usuarios podem twettar (textos) sobre algo, alguém etc. Muitos twettes são ofensivos, outros são
textos de esperança e alegria e alguns são apenas informativos - neutros. O Twitter disponibiliza uma API onde desenvolvedores podem requisitar os twetts da plataforma - obedecendo certas regras. Os twetts são eventos - unbounded - gerados de forma infinita e sem uma dependência de tempo de geração. Para classificarmos os twettes em positivo, negativo e neutro é preciso tratar e formular uma arquitetura voltada a processamento de streaming e uma plataforma final para o usuario com alta velocidade de busca textual, e também não menos importante, é preciso de um algoritmo que classifique os twettes em suas respectivas classes. O tratamento de textos - strings- merece uma atenção especial, pois técnicas de Machine Learning são especiais para atender palavras. No presente projeto foi utilizado o algoritmo de Naive Bayes para classificar os twetts.

A Imagem a seguir representa a arquitetura utilizada:

![Project Architecture](Images/archt.png)


* Topico: eventcrud.twitter.json
* Ler topico: sudo  /usr/local/kafka/bin/kafka-console-consumer.sh --topic eventcrud.twitter.json --bootstrap-server localhost:9092