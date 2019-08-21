#!/usr/bin/env python
import pika
import uuid


class Pipeline:

    def __init__(self):
        self.queue_origem = 'fila_eventos_a_processar'
        self.queue_destino = 'fila_eventos_a_buscar_regras'

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

        self.response = None
        self.corr_id = None
        self.delivery_tag = None

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_origem)
        self.channel.queue_declare(queue=self.queue_destino)

        # cria fila de callback exclusivo para BOT, e consumí-lo
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        print(' [x] Criada fila', self.callback_queue, ' para callback de evento + regras')

        self.channel.basic_consume(self.callback_queue,
                                   self.on_rpc_callback,
                                   auto_ack=False)

        self.channel.basic_qos(prefetch_count=1)
        # self.channel.basic_consume('fila_eventos_a_processar', self.on_response)

        print(" [x] Aguardando callback de eventos em", self.callback_queue)
        # self.channel.start_consuming()

    # no consumo da fila de callback
    def on_rpc_callback(self, ch, method, props, body):
        print(' [CALLBACK] obtido callback response com corr_id', props.correlation_id)
        if self.corr_id == props.correlation_id:
            self.response = body
            print(' [CALLBACK] obtido response:', body)
            # persistir evento+regras na base de dados

            # ack no evento da "fila_callback"
            ch.basic_ack(delivery_tag=method.delivery_tag)

            # ack no evento da 'fila_eventos_a_processar'
            self.channel.basic_ack(delivery_tag=self.delivery_tag)

            print(' [CALLBACK] confirmados eventos')
            print()

    # publicar na fila "eventos_a_buscar_regras"
    def send_to_process(self, evt):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        print(' [x] publicando evento em', self.queue_destino, 'com corr_id', self.corr_id)
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_destino,
            body=evt,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            )
        )
        # print(' [x] aguardando response')
        # while self.response is None:
        #     self.connection.process_data_events()
        # print(' [x] obtido response')
        return self.response

    def on_regra_recebida(self, ch, method, props, body):
        self.delivery_tag = method.delivery_tag

        event = str(body)
        print(' [x] evento obtido', str(event))

        # publicar evento na fila 'eventos_a_buscar_regras', com propriedade de fila de callback criada
        self.send_to_process(event)

    # consumir evento da "fila_eventos_a_processar"
    def consume(self):
        # consumir 'fila_eventos_a_processar'
        self.channel.basic_consume(self.queue_origem,
                                   self.on_regra_recebida,
                                   auto_ack=False)

        self.channel.basic_qos(prefetch_count=1)

        print(" [x] Awaiting RPC requests")
        print(" [x] Aguardando  eventos à processar em", self.queue_origem)
        print()
        self.channel.start_consuming()


# consumir evento da "fila_eventos_a_processar"
# no consumo da fila de callback
#   - criar fila de callback, e consumí-la;
#   - quando callback recebido:
#       - persistir evento+regras na base de dados
#       - ack no evento da "fila_callback"
#       - ack no evento da "fila_eventos_a_processar"
#   - publicar na fila "eventos_a_buscar_regras"


# quando obtido evento da "fila_eventos_a_processar"
# event_example = '{"id"; 1, "descricao": "Evento teste" }'

pipeline = Pipeline()
# consumir 'fila_eventos_a_processar'
pipeline.consume()
