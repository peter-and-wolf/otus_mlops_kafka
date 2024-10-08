import time

import typer
from typing_extensions import Annotated
from confluent_kafka import Consumer # type: ignore

import cfg

OFFSET = -1
MESSAGE_TO_CONSUME = 4

def on_assign(consumer, partitions):

  if OFFSET >= 0:
    for part in partitions:
      part.offset = OFFSET

  consumer.assign(partitions)

  for part in consumer.committed(partitions):
    print(part)
  
  print('-----')

def main(topic: Annotated[str, typer.Option()] = 'payments',
         group: Annotated[str, typer.Option()] = 'otus-consumer',
         limit: Annotated[int | None, typer.Option(min=1)] = None,
         auto_commit: Annotated[bool, typer.Option()] = False,
         manual_commit: Annotated[bool, typer.Option()] = True) -> None:

  condition = cfg.get_condition(limit)

  consumer = Consumer({
    'bootstrap.servers': cfg.BOOTSTRAP_SERVERS,
    'group.id': group,
    'auto.offset.reset': 'earliest', 
    'enable.auto.commit': auto_commit,
  })

  try:
    consumer.subscribe([topic], on_assign=on_assign)

    num = 0
    while condition(num):
      msg = consumer.poll(1.0)

      if msg is None:
        continue
      if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

      print(f'Received message {msg.value().decode("utf-8")} at {msg.offset()}')

      num += 1
      
      if not auto_commit and manual_commit:
        consumer.commit(asynchronous=False)
  
  finally:
    consumer.close()


if __name__ == '__main__':
  typer.run(main)
