#!/usr/bin/env python
import pika
import sys


# Abre uma conexão com o RabbitMQ
# Declara uma exchange exclusiva, do tipo 'topic' e com nome randômico
# Obtém a binding_key por parâmetro, senão define um parâmetro
# Abre um canal de comunicação para recepção de logs
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs',
                         exchange_type='topic')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

binding_keys = sys.argv[1:]
if not binding_keys:
    binding_keys = 'app_name.error'
    # sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    # sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(exchange='topic_logs',
                       queue=queue_name,
                       routing_key=binding_key)

print(' [x] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(' [x] %r:%r' % (method.routing_key, body))


channel.basic_consume(queue_name,
                      callback,
                      auto_ack=True)

channel.start_consuming()
