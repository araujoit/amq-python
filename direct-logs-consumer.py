#!/usr/bin/env python
import pika
import sys


# Abre conexão com o RabbitMQ
# Declara um exchange do tipo direct
# Declara uma queue exclusiva, com nome randômico
# Para cada severidade em um array:
# 1. conecta com a queue exclusiva
# Inicia consumo das queues
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declara a exchange do tipo fanout: envia as novas mensagens para todas as queues conectadas/conhecidas
channel.exchange_declare(exchange='direct_logs',
                         exchange_type='direct')

# Declara uma queue exclusiva com um nome randômico
result = channel.queue_declare(exclusive=True)
# Obtêm o nome da queue criada
queue_name = result.method.queue
# Efetua o bind da queue com a exchange

severities = ["ERROR"]

if not severities:
    print("Sem níveis de logs setados.")
    sys.exit(1)

for severity in severities:
    channel.queue_bind(exchange='direct_logs',
                       queue=queue_name,
                       routing_key=severity)

print(' [*] Aguardando pelos logs. Para sair pressione CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r" % body)


# Efetua consumo da queue
channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
