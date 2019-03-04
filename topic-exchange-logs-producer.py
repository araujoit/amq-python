#!/usr/bin/env python
import pika
import sys

# Abre uma conexão com o RabbitMQ
# Declara uma exchange, do tipo 'topic' e com nome randômico
# Define um parâmetro de routing_key, caso não tenha sido recebido por parâmetro
# Define uma mensagem para envio, caso não tenha sido recebido por parâmetro
# Envia o log
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs',
                         exchange_type='topic')

routing_key = sys.argv[1] if len(sys.argv) > 2 else 'app_name.error'
message = ' '.join(sys.argv[2:]) or 'Hello World!'

channel.basic_publish(exchange='topic_logs',
                      routing_key=routing_key,
                      body=message)

print(' [x] Sent %r:%r' % (routing_key, message))
connection.close()
