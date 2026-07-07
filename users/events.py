import os
import json
import pika
import logging

logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')

def _publish_event(event_name: str, user_id: int, username: str):
    try:

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        queue = channel.queue_declare(queue='user_events')

        message = {'event': event_name, 'user_id': user_id, 'username': username}

        message = json.dumps(message)

        channel.basic_publish(exchange='', routing_key='user_events', body=message)
        connection.close()

    except Exception as e:
        logger.error(f"Failed to publish event '{event_name}': {e}")
        
def publish_user_registered(user_id: int, username: str):
    _publish_event('user.registered', user_id, username)

def publish_user_updated(user_id: int, username: str):
    _publish_event('user.updated', user_id, username)

def publish_user_deleted(user_id: int, username: str):
    _publish_event('user.deleted', user_id, username)