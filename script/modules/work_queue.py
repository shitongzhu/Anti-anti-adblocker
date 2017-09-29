#!/usr/bin/env python
import pika


def read_locallist(path_to_file):
    f = open(path_to_file, 'r')
    lst = f.readlines()
    return map(lambda lne: lne.strip(), lst)


def submit_urllist():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)

    local_urllist = read_locallist('../../res/urllist1.txt')

    for url in local_urllist:
        if url == '':
            continue
        message = url
        channel.basic_publish(exchange='',
                              routing_key='task_queue',
                              body=message,
                              properties=pika.BasicProperties(
                                 delivery_mode=2, # make message persistent
                              ))
        print(" [x] Sent %r" % message)
    connection.close()
