#!/usr/bin/env python
import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declara a exchange do tipo fanout: envia as novas mensagens para todas as queues conectadas/conhecidas
channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')

# Publica a mensagem na exchange ao invés da QUEUE
message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='logs',
                      routing_key='',
                      body=message)
print(" [x] Enviada %r" % message)
connection.close()
