# Twitter - Streaming de Análise Sentimental

O Projeto abaixo trata de resolver o Teste da IBM, onde o objetivo é criar uma arquitetura distribuida, escalável para
analisar os textos - unbounded data - produzidos pelo Twitter (pt-br). O problema em questão se encontra na família de streaming
processing, onde os dados vindos de uma fonte que gera dados infinitos, sem padrão de tempo definido, ou seja unbounded data.

O Processamento de Streaming vem ganhando cada vez mais importancia, pois os metodos de ETL com batch processing engine já não são capazes de suportar a natureza dos dados em streaming. Para isso novas tecnologias e arquiteturas são formuladas para melhor atender a este novo cenario.

O que é Streaming data ?

--- <respodner>


- [x] Criar o Produtor para enviar os eventos para o Kafka
- [X] Configurar o Streaming Processor Faust
- [X] Desenvolver um modelo de Machine Learning e testar a acurácia 
- [X] Instalar e Configurar o ElasticSearch + Kibana (Cloud ou VM ou Docker - cuidado com dockers)
- [X] Conectar o Faust com Elasticsearch 
- [X] Desenvolver Dashboards em Real-Time e Canvas
- [ ] Integrar a aplicação - Produtor e Consumidor - em Docker Containers
- [X] Garantir Escalabilidade em Produtores e Consumidores
- [ ] Futuras contribuições - Apache Druid e instalar o Logstash + MetricBeats (Monitorar minha aplicação)


## Pre-requisitos

Os seguintes requisitos são necessários para rodar este projeto:

* Docker
* Python 3.7
* Kafka + Schema Registry + KSQL
* ELK
* Faust
* SkLearn
* Acesso a um computador de no minimo 16gb+ RAM e 4-core CPU.
* Acesso a um broker Kafka (VM no caso disponibilizada ou então um docker).
* Acesso ao servidor em cloud do ElasticSearch.


## Descrição

O Twitter é uma rede social onde os usuarios podem twettar (textos) sobre algo, alguém etc. Muitos twettes são ofensivos, outros são
textos de esperança e alegria e alguns são apenas informativos - neutros. O Twitter disponibiliza uma API onde desenvolvedores podem requisitar os twetts da plataforma - obedecendo certas regras. Os twetts são eventos - unbounded - gerados de forma infinita e sem uma dependência de tempo de geração. Para classificarmos os twettes em positivo, negativo e neutro é preciso tratar e formular uma arquitetura voltada a processamento de streaming e uma plataforma final para o usuario com alta velocidade de busca textual, e também não menos importante, é preciso de um algoritmo que classifique os twettes em suas respectivas classes. O tratamento de textos - strings- merece uma atenção especial, pois técnicas de Machine Learning são especiais para atender palavras. No presente projeto foi utilizado o algoritmo de Naive Bayes para classificar os twetts.

A Imagem a seguir representa a arquitetura utilizada:

![Project Architecture](Images/archt.png)

### Passo 1: Instalar o Kafka/Zookeeper e Criar Topico:

Um docker-compose foi fornecido para instalar o Kafka e todas sua estrutura. Porém no caso, aconselho a usar o Kafka dedicado em uma VM
para se ter um aproveitamento melhor e controle fino sobre a JVM, Swap, GarbageCollect e I/O measurements. Foi fornecido tanto a versão
em docker como a VM que eu utilizei. Para instalar na Cloud o Kafka, requer uma VM com mais de 1GB, o que deixou meu projeto inviavel financeiramente para criar Brokers em Cloud.

Apache Kafka utiliza o Zookeeper (versões antigas) para armazenar o metadata do Kafka cluster, também
os consumer client details. Para Instalar o Zookeeper os pré-requisitos são:Java ->

```bash
sudo apt install openjdk-8-jdk
java -version
```

{VERSION} = zookeeper-3.4.14
{FILE} = zookeeper-3.4.14.tar.gz

```bash
sudo wget http://mirror.cc.columbia.edu/pub/software/apache/zookeeper/{VERSION}/{FILE}
#
tar -zxf {FILE}
mv zookeeper-3.4.6 /usr/local/zookeeper
mkdir -p /var/lib/zookeeper
cp  /usr/local/zookeeper/conf/zoo_sample.cfg  /usr/local/zookeeper/conf/zoo.cfg 
export JAVA_HOME={/usr/path/JAVA_VERSION}
```

Para um maior detalhamento do Zookeeper aconselho ler o Zookeeper da O'reilly, muito bom, melhor até que a documentação.

Com o Zookeeper, você pode instalar o Apache Kafka pelo site http://kafka.apache.org/downloads.html

```bash
tar -zxf kafka_2.{VERSION}.tgz
mv kafka_2.{VERSION} /usr/local/kafka
mkdir /tmp/kafka-logs
/usr/local/kafka/bin/kafka-server-start.sh -daemon
/usr/local/kafka/config/server.properties
```

Para os comandos iniciais do Kafka eu forneci alguns arquivos em Bash, na pasta de VirtualMachines

```bash
sudo ./start_server.sh or
sudo ./start_topics.sh
```

Topicos criados:

```bash
cd ~
sudo .\creat_topics eventcrud.twitter.json
sudo  /usr/local/kafka/bin/kafka-console-consumer.sh --topic eventcrud.twitter.json --bootstrap-server localhost:9092
```

Aconselho sempre a revisão detalhada na hora de criar topicos, não aconselho a sua automatização, é preciso muito estudo antes de sair
escolhendo as configs, faça testes de compressão e analise bem seu benchmarking, para melhorar sua performance saiba equilibrar:
* Brokes -> Replication -> Group Consumer -> Numero de Prod/Cons

### Passo 2: Configurar Producer:

Para rodar o Produtor existem os seguintes arquivos:

1. logwitter: É o core do produtor, onde a API do twitter é utilizada de forma assincrona utilizando uma classe desenvolvida pela
biblioteca tweepy, com alguns topicos escolhidos para o projeto. Ao mesmo tempo que a classe de streaming está consumindo tweets ela envia para um tópico Kafka os eventos filtrados. O formato que melhor se adequa para processamento de streaming é o Avro.

2. eventtwiiter: É o meu produtor de eventos do twitter, No caso rodando localmente eu defino um tempo de streaming consuming baseado na variavel self.limit.

```bash
python logwitter.py
```


### Passo 3: Configurar Faust:

O Faust é uma biblioteca de processamento de streaming, herdando ideias do Kafka Stream para o Python. Ele usa o robinhood para construir
um sistema distribuido de alta performance e em tempo real -> piplines. [Faust](https://faust.readthedocs.io/en/latest/)

O Faust funciona baseado no modelo de atores (actor models - processador de fluxo pode ser executado simultaneamente em muitos núcleos de CPU e em centenas de máquinas ao mesmo tempo.), porém se você usa o Celery, você pode pensar no Faust como sendo não apenas um executador de tarefas, mas ele mantem o histórico de tudo o que aconteceu até agora. Ou seja, as tarefas (“agentes” no Faust) podem manter o estado e também replicar esse estado para um cluster de instâncias do trabalhador Faust.

Graças ao Faust o nosso programa pode ser escalavel de maneira tranquila - Tanto multicores quanto multimáquinas.

Para mais detalhes do faust -> [detalhes](https://faust.readthedocs.io/en/latest/introduction.html#design-considerations)


* Executando o consumidor realizando ao mesmo tempo a classificação dos textos(tweets):

```bash
faust -A faust_stream worker -l info
```


### Passo 3: Classificador de Tweets:

Primeira parte para começar a desenvolver o modelo de ML, primeiro eu coletei alguns twettes do streaming API e salvando em um json apenas com o intuito de analisar com mais calma. Através do Kaggle, eu busquei um arquivo de treinamento e usando meus arquivos jsons para um set de teste. Em um problema de text e ML, a primeira coisa que vem na mente para começar o processamento do modelo é o pre-processamento dos twettes. No caso 3 funções para pre-processar foram utilizadas: Remover StopWords, limpara os textos - remover url e Steaming.

Os primeiros modelos testados foram o MultinomialNB e RandomForest que apresentaram bons resultados: metrica de predição de 0.866 (No notebook existem as metricas utilizadas). Por fim eu testei o Naive Bayes (eu ja havia testado esse algoritmo antes no meu estagio e ja sabia de antemão uma previsão boa).

O modelo escolhido foi o Naive Bayes devido sua boa performance - fator decisivo para streaming data - e bons resultados de metrica. Por fim, o modelo foi salvo em um arquivo binario - pickle - e quando o faust inicia o processamento de dados ele ja lê o pickle.


### Passo 4: Real-Time Dashboards:

Por fim, os twetts - eventos - ja classificados pelo Faust são enviados para o ElasticSearch, onde através do Kibana podemos analisar
os eventos no Dashboards:

![Dashboards](Images/Dashboard.PNG)


![Relatorios](Images/Relatorio.PNG)


Podemos ter uma visão em tempo-real dos eventos classificados.


### Video - Teste:

Existe um video que mostra a demonstração do projeto completo.