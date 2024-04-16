import faker
from confluent_kafka import Producer


MESSAGE_NUMBER = 12


def delivery_report(error, message):
  if error is not None:
    print(f'Message delivery failed: {error}')
  else:
    print(f'Message delivered to {message.topic()}[{message.partition()}], offset={message.offset()}')


if __name__ == '__main__':
  
  f = faker.Faker()

  try:  
    producer = Producer({
      'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
      'retries': 2,
      'acks': 'all',
      'enable.idempotence': False,
    })

    topic_name = 'names'

    for i in range(MESSAGE_NUMBER):
      producer.produce(topic_name, f'{i}: {f.name()}', key=None, callback=delivery_report)

    # Serve delivery callback queue.
    # NOTE: Since produce() is an asynchronous API this poll() call
    #       will most likely not serve the delivery callback for the
    #       last produced message.
    producer.poll(0)

    # Wait until all messages have been delivered
    producer.flush()
  except:
    print('Have a nive day!')