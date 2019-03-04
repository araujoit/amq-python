#!/usr/bin/env python
import pika


# Abre conexão com o RabbitMQ
# Declara o exchange do tipo fanout, com foco em logs
# Declara a queue exclusiva
# 'Escuta' a queue, e quando recebe a mensagem printa na tela
def callback(ch, method, properties, body):
    print(" [x] %r" % body)


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declara a exchange do tipo fanout: envia as novas mensagens para todas as queues conectadas/conhecidas
channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')

# Declara uma queue exclusiva com um nome randômico
result = channel.queue_declare(exclusive=True)
# Obtêm o nome da queue criada
queue_name = result.method.queue
# Efetua o bind da queue com a exchange
channel.queue_bind(exchange='logs',
                   queue=queue_name)

print(' [*] Aguardando pelos logs. Para sair pressione CTRL+C')

# Efetua consumo da queue
channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
