#!/usr/bin/env python
import pika
import time


# Abre conexão com o RabbitMQ
# Declara queue 'durable'
# Configura a queue para processar apenas uma mensagem por vez
# Inicia consumo da queue
# Quando recebe mensagem:
# 1. printa quantidade de pontos na mensagem
# 2. envia ack para o RabbitMQ
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
channel.basic_consume('task_queue',
                      callback)

print("Start consuming")
channel.start_consuming()
