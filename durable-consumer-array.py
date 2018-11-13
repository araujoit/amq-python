#!/usr/bin/env python
import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    # Aguarda a quantidade de segundos referentes a quantidade de .
    seconds_to_wait = body.count(b'.')
    print("Contains", seconds_to_wait, "dots.", "Waiting", seconds_to_wait, "seconds")
    time.sleep(seconds_to_wait)
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Dis ao RabbitMQ para não despachar uma nova mensagem para o worker até que o anterior tenha sido processado e reconhecido (acknowledged).
# Em vez disso, será despachado para o próximo funcionário que ainda não esteja ocupado.
print("Configuring consumer to process only one message by time")
channel.basic_qos(prefetch_count=1)

print("Configuring callback method")
channel.basic_consume(callback,
                      queue='task_queue')

print("Start consuming")
channel.start_consuming()