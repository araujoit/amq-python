#!/usr/bin/env python



# Abre conexão com o rabbit, ouvindo a queue 'rpc_queue'.
# Quando recebe a distribuição de um número para processamento:
# 1. Calcula o fibonacci do número
# 2. Publica o resultado na fila recebida como parâmetro
# 3. Envia um 'ack' para o RabbitMQ
# Fecha a conexão
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='rpc_queue')


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def on_request(ch, method, props, body):
    n = int(body)

    print(" [.] fib(%s)" % n)
    # ch.basic_ack(delivery_tag=method.delivery_tag)
    response = fib(n)
    print(" [.] fib value for", n, "=", response)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id= \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='rpc_queue')

print(" [x] Awaiting RPC requests")
channel.start_consuming()
