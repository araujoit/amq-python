#!/usr/bin/env python
import pika


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

queue = 'fila_eventos_a_processar'
channel.queue_declare(queue=queue)

event_example = '{"id"; 1, "descricao": "Evento teste" }'
channel.basic_publish(
    exchange='',
    routing_key=queue,
    body=event_example,
)

print('Publicado:', event_example)

