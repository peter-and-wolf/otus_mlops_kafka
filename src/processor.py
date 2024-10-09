import time
from datetime import datetime
import json
import pprint

import numpy as np
import typer
from typing_extensions import Annotated
from confluent_kafka import Consumer, Producer, Message # type: ignore

import cfg


def aggregate(message: list[Message]):
  stats = {k: np.zeros(2) for k in cfg.NAMES}
  for msg in message:
    msg = json.loads(msg.value().decode("utf-8"))
    stats[msg['name']] += np.array([msg['amount'], 1.])
  
  return {k: 0. if v[1] == 0 else float(v[0]/v[1]) for k,v in stats.items()}


def main(in_topic: Annotated[str, typer.Option()] = 'payments',
         out_topic: Annotated[str, typer.Option()] = 'payments_aggregated',
         window: Annotated[int, typer.Option(min=1)] = 10,
         group: Annotated[str, typer.Option()] = 'otus-consumer') -> None:

  consumer = Consumer({
    'bootstrap.servers': cfg.BOOTSTRAP_SERVERS,
    'group.id': group,
    'auto.offset.reset': 'earliest', 
    'enable.auto.commit': True,
  })

  producer = Producer({
    'bootstrap.servers': cfg.BOOTSTRAP_SERVERS,
    'retries': 1,
    'acks': 1,
    'enable.idempotence': False,
  })

  try:
    consumer.subscribe([in_topic])

    start = time.time() 
    messages = []

    while True:

      msg = consumer.poll(1.0)

      if msg is None:
        continue
      if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

      messages.append(msg)

      lap = time.time()
      if lap - start >= window:
        aggregated = json.dumps(
          aggregate(messages), 
          indent=2
        )

        producer.poll(0)
        producer.produce(
          topic=out_topic, 
          value=aggregated, 
          key=None, 
        )

        print(f'--- {datetime.fromtimestamp(start)} ---')
        print(aggregated)
        messages = []
        start = lap
  
  finally:
    consumer.close()
    producer.flush()


if __name__ == '__main__':
  typer.run(main)
