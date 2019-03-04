#!/usr/bin/env python
import pika
import uuid

# Abre conexão com o rabbit
# Envia um número para a queue 'rpc_queue'
# 'Escuta' a queue onde o response será publicado
# Quando recebe a resposta do cálculo, printa na tela e fecha a conexão
class FibonacciRpcClient(object):
    def __init__(self):
        self.queue = 'rpc_queue'
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        print(' [x]Listening asnwer on', self.callback_queue)
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return int(self.response)

fibonacci_rpc = FibonacciRpcClient()

print(" [x] Requesting fib(30) on", fibonacci_rpc.queue)
response = fibonacci_rpc.call(30)
print(" [.] Got %r" % response)