import json
import time
import random

import typer
from typing_extensions import Annotated
from confluent_kafka import Producer # type: ignore

import cfg


def delivery_report(error, message):
  if error is not None:
    print(f'Message delivery failed: {error}')
  else:
    print(f'Message delivered to {message.topic()}[{message.partition()}], offset={message.offset()}')


def main(topic: Annotated[str, typer.Option()] = 'payments',
         limit: Annotated[int | None, typer.Option(min=1)] = None, 
         timeout: Annotated[float, typer.Option(min=0.)] = .5) -> None:
  
  try:
    producer = Producer({
      'bootstrap.servers': cfg.BOOTSTRAP_SERVERS,
      'retries': 2,
      'acks': 'all',
      'enable.idempotence': False,
    })

    for _ in cfg.get_range(limit):
      
      # Polls the producer for events and 
      # calls the corresponding callbacks
      producer.poll(0)
      
      # Produce message to topic.
      producer.produce(
        topic=topic, 
        value=json.dumps({
          'name': random.choice(cfg.NAMES),
          'amount': random.randint(1, 1000)
        }), 
        key=None, 
        callback=delivery_report
      )

      time.sleep(timeout)

  finally:
    # Wait for all messages in the 
    # Producer queue to be delivered.
    producer.flush()


if __name__ == '__main__':
  typer.run(main)