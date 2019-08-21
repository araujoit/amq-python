#!/usr/bin/env python
import pika


class BuscadorRegras:

    def __init__(self):
        self.queue_origem = 'fila_eventos_a_buscar_regras'
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_origem)

        self.channel.basic_consume(self.queue_origem,
                                   self.on_callback_response,
                                   auto_ack=False)

    def on_callback_response(self, ch, method, props, body):
        event = str(body)
        print(' [x] obtido evento', event)

        # TODO: buscar regars
        print(' [x] buscadas regras')
        print(' [x] atualizados eventos')
        populated_event = event

        reply_to_queue = str(props.reply_to)

        self.channel.basic_publish(
            exchange='',
            routing_key=reply_to_queue,
            body=str(populated_event),
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
        )

        # ack no evento da 'fila_eventos_a_buscar_regras'
        ch.basic_ack(delivery_tag=method.delivery_tag)

        print()
        print(" [x] Aguardando  eventos à processar em", self.queue_origem)

    def consume(self):
        print(" [x] Aguardando  eventos à processar em", self.queue_origem)
        self.channel.start_consuming()


buscador = BuscadorRegras()
buscador.consume()
