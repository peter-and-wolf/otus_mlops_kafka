# MLOps, №13 "Сбор данных на потоке, Kafka"

## Запуск кластера

`zk-kafka-cluster.yaml` включает:

- "Тренировочный" кластер Kafka из трех брокеров;
- "Тренировочный" кластер Zookeeper из трех нод;
- [Kafka UI](https://docs.kafka-ui.provectus.io/) от provectuslab – web-интерфейс для управления кластером Kafka;
- [ksqldb](https://ksqldb.io/) – специальная база данных, которая умеет работатьс  потоковыми данными из топиков Kafka;
- ksqldb-cli – интерфейс командной строки (консоль) для взаимодействия с ksqldb;

Чтобы все запустить, выполните:

```
docker-compose -f zk-kafka-cluster.yaml up
```

## Управление кластером

### Через командную строку

Выполните команду:

```
docker exec -it kafka-broker1 bash 
```

Окажетесь "внутри" контейнера, в котором запущен первый брокер Kafka. Теперь можно запускать стандартные утилиты командной строки, предназначеные для управления кластером. 

Например, так:

```
kafka-topics --create --topic test --partitions 3 --replication-factor 3 --bootstrap-server kafka1:19092
```
можно создать топик с именем `test`, в котором три партиции, и уровень репликации которого равен трем.

Так:

```
kafka-topics --describe --topic test --bootstrap-server kafka1:19092
```

можно вывести на экран информацию о топике `test`.

А так:

```
kafka-configs --bootstrap-server kafka1:19092 --alter --entity-type topics --entity-name test --add-config min.insync.replicas=2
```

можно переконфигурировать топик, указав, что параметр `min.insync.replicas` (минимальное количество брокеров, которые должны прислать подтверждение о записи сообщения) теперь равен двум. 

### Через Kafka UI

По адресу localhost:8282 доступен приятный web-интерфейс, который позволяет выполнять основные операции с кластером чуть комфортнее, чем командная строка. 

## ksqldb

Чтобы попасть в консоль, выполните:

```
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
```

Теперь можно исполнять запросы и команды ksqldb.

Например, создать ksqldb-поток (stream), а вместе с ним и соответствующий топик в кластере Kafka, можно так:

```
CREATE STREAM payments (name VARCHAR, amount INTEGER)
  WITH (kafka_topic='payments', value_format='json', partitions=1);
```

Теперь можно читать сообщения из потока SQL-like синтакисиом. Например, 

```
SELECT ROWOFFSET, * FROM payments EMIT CHANGES;
```

Или с фильтрами в WHERE:

```
SELECT ROWOFFSET, * FROM payments WHERE name='Bob' EMIT CHANGES;
```

Данные можно агрегировать. Такой запрос:

```
SELECT name, SUM(amount) from payments GROUP BY name EMIT CHANGES;
```

Запустит агрегацию от текущего смещения (offset) до момента остановки запроса. То есть ksqldb будет считывать новые сообщения из топика и "доагрегирповать" их к текущему результату, который и напечатает на экране. И так до тез пор, пока вы не остановите запрос. 

Вот так реализуется агрегация в окне:

```
SELECT name, SUM(amount) from payments
  WINDOW TUMBLING (SIZE 10 SECONDS)
  GROUP BY name EMIT CHANGES;
```

Теперь ksqldb будет читать все сообщения, которые пришли за 10 секунд (SIZE 10 SECONDS), агрегировать результаты, показывать из вам и открывать новое 10-ти секундное окно. 

А вот так можно создать таблицу (физически – новый топик в Kafka), источником данных для которой будет запрос в поток:

```
CREATE TABLE payments_table AS
  SELECT name, count(*) AS cnt, sum(amount) AS sum, avg(amount) AS avg
  FROM payments GROUP BY name EMIT CHANGES;
```

Теперь можно запрашивать саму таблицу:

```
SELECT * FROM payments_table;
```

и получать свежую агрегированную сводку.

------

P.S. Спасибо. Живите долго и процсетайте!



