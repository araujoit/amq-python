#!/usr/bin/env python
# -*- coding: utf-8 -*-
import faker
import pika
import time
import json
import random


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

queue = 'fila_eventos_a_processar'
channel.queue_declare(queue=queue)

faker_instance = faker.Faker()

departamentos_list = ['Urgencia', 'Entrada', 'Triagem', faker_instance.name(), faker_instance.name(),
                        faker_instance.name(), faker_instance.name(), faker_instance.name(), faker_instance.name(),
                        faker_instance.name(), faker_instance.name(), faker_instance.name(), faker_instance.name(),
                        faker_instance.name(), faker_instance.name(), faker_instance.name(), faker_instance.name(),
                      ]
event_list_example = []

for qtd in range(10):
    event_list_example.append(
        {
            'descricao': faker_instance.text(),
            'propriedades': {
                'nome': faker_instance.name(),
                'Departamento': random.choice(departamentos_list)
            }
        }
    )

while(True):
    event_example = random.choice(event_list_example)

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(event_example),
    )

    print('Publicado:', event_example)

    time.sleep(0.2)