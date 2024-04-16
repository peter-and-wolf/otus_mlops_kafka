import time

from confluent_kafka import Consumer

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


if __name__ == '__main__':

  consumer = Consumer({
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'group.id': 'beatles',
    'auto.offset.reset': 'earliest', 
    'enable.auto.commit': True,
  })

  try:
    consumer.subscribe(['names'], on_assign=on_assign)

    i = 0
    while i < MESSAGE_TO_CONSUME:

      msg = consumer.poll(1.0)

      if msg is None:
        continue
      if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

      print(f'Received message {msg.value().decode("utf-8")} at {msg.offset()}')
      i += 1

      consumer.commit(asynchronous=False)

  except KeyboardInterrupt:
    print('Have a nice day!')
  finally:
    consumer.close()
