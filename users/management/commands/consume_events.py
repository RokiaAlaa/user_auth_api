import os
import json
import pika
from datetime import datetime
from django.core.management.base import BaseCommand

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')

class Command(BaseCommand):

    def handle(self, *args, **options):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        queue = channel.queue_declare(queue='user_events')

        def callback(ch, method, properties, body):
            data = json.loads(body)
            line = f"{datetime.utcnow()} - Event: {data['event']} | User: {data['username']} (ID: {data['user_id']})\n"

            with open('logs/user_events.log', 'a') as f:
                f.write(line)

            print(line)

        channel.basic_consume(queue='user_events', on_message_callback=callback, auto_ack=True)

        print('Waiting for events...')
        channel.start_consuming()