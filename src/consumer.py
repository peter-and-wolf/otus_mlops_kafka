import typer
from typing_extensions import Annotated
from confluent_kafka import Consumer # type: ignore

import cfg


def on_assign(offset: int | None, consumer, partitions):

  if offset is not None and offset >= 0:
    # for all partitions
    for part in partitions:
      # force to set offset manually
      part.offset = offset

  consumer.assign(partitions)

  print('--- Partitions to consume ---')
  for part in consumer.committed(partitions):
    print(part)
  print('------')


def main(topic: Annotated[str, typer.Option()] = 'payments',
         group: Annotated[str, typer.Option()] = 'otus-consumer',
         offset: Annotated[int | None, typer.Option(min=0)] = None,
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
    consumer.subscribe([topic], 
      on_assign=lambda c, p: on_assign(offset, c, p))

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
