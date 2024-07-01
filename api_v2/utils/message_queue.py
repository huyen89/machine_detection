import json
import pika
import pika.exceptions
from django.conf import settings


def publish_submission_to_queue(submission_id):
    MAX_ATTEMPT = 5
    attempt = 0
    while True:
        try:
            if attempt > MAX_ATTEMPT:
                break

            credentials = pika.PlainCredentials(settings.RABBITMQ_SETTINGS['username'], settings.RABBITMQ_SETTINGS['password'])
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_SETTINGS['host'], credentials=credentials))
            channel = connection.channel()

            channel.queue_declare(queue=settings.RABBITMQ_SETTINGS['machine_detection_queue_name'], durable=True)

            data = {
                "submission_id": submission_id
            }
            channel.basic_publish(exchange='',
                                  routing_key='machine_detection',
                                  body=json.dumps(data),
                                  properties=pika.BasicProperties(
                                      delivery_mode=pika.DeliveryMode.Persistent
                                  ))
            print(f"Sent submission ID: {submission_id}")
            break
        except pika.exceptions.AMQPConnectionError:
            attempt += 1
            continue
        except pika.exceptions.AMQPChannelError:
            attempt += 1
            continue

    if attempt > MAX_ATTEMPT:
        print(f"Cannot not publish submission ID: {submission_id}")
        return False

    return True
