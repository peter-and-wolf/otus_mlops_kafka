import time
import json
import random

from confluent_kafka import Producer


NAMES = names = ['Alice', 'Bob', 'Mallory', 'Carol', 'Chuck', 'Peggy', 'Victor', 'Trent']
TOPIC_NAME = 'payments'


def delivery_report(error, message):
  if error is not None:
    print(f'Message delivery failed: {error}')
  else:
    print(f'Message delivered to {message.topic()}[{message.partition()}], offset={message.offset()}')


if __name__ == '__main__':
  
  producer = Producer({
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'retries': 0,
    'acks': 0,
    'enable.idempotence': False,
  })

  try:
    while True:
      msg = {
        'name': random.choice(NAMES),
        'amount': random.randint(1, 1000)
      }

      producer.produce(TOPIC_NAME, json.dumps(msg), key=None, callback=delivery_report)

      # Serve delivery callback queue.
      # NOTE: Since produce() is an asynchronous API this poll() call
      #       will most likely not serve the delivery callback for the
      #       last produced message.
      producer.poll(0)

      time.sleep(.5)
  except: 
    print('Have a nice day')
  finally:
    # Wait until all messages have been delivered
    producer.flush()