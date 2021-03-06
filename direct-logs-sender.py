#!/usr/bin/env python
import pika
import time

# A cada 2 segundos:
# Abre conexão com o RabbitMQ
# Declara um exchange do tipo direct
# Publica uma mensagem em uma severidade
# Encerra a conexão
while True:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declara a exchange do tipo fanout: envia as novas mensagens para todas as queues conectadas/conhecidas
    channel.exchange_declare(exchange='direct_logs',
                             exchange_type='direct')

    severity = "ERROR"
    # severity = "INFO"
    message = "Lorem ipsum exception!"
    channel.basic_publish(exchange='direct_logs',
                          routing_key=severity,
                          body=message)

    print(" [x] Sent %r:%r" % (severity, message))
    connection.close()
    print("Waiting 2 seconds")
    time.sleep(2)
