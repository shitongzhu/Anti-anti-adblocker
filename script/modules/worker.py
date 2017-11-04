#!/usr/bin/env python
import pika
from script.conf.param import *

url_fetched = ''


def fetch_url():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=DISPATCHER_HOST))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        global url_fetched
        url_fetched = body
        channel.stop_consuming()

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback,
                          queue='task_queue')
    channel.start_consuming()
    return url_fetched
#test
