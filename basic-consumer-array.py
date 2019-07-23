#!/usr/bin/env python
import pika


# Abre conexão com o RabbitMQ
# Declara uma queue
# Inicia consumo da queue

# Callback function
def callback(ch, method, properties, body):
    print(" [x] Recebido %r" % body)


# Definindo connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# Opening connection channel
channel = connection.channel()

queue_name = 'hello'
# Declaring queue
channel.queue_declare(queue=queue_name)
# Defining consumer function, queue and authomatic ack
channel.basic_consume(queue_name,
                      callback,
                      auto_ack=True)
print(' [*] Aguardando por mensagens. Para sair digite CTRL+C')
channel.start_consuming()
