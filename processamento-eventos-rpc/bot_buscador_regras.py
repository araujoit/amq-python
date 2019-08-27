#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pika
import json
import mysql.connector


class Database:
    def __init__(self):
        self.mydb = mysql.connector.connect(host="localhost", port=3316,
                                            database='eventos_database',
                                            user="root",
                                            passwd="123456")
        print(' [INIT] Conectado ao mysql')

    def fetch_regras(self, json_event):
        mycursor = self.mydb.cursor()

        propriedades = json_event['propriedades']

        regras = []
        for campo_nome, campo_valor in propriedades.items():
            query = 'SELECT id_regra FROM tb_regra_campos WHERE campo_nome="%s" AND campo_valor="%s"' \
                    % (campo_nome, campo_valor)
            mycursor.execute(query)

            myresult = mycursor.fetchall()

            for x in myresult:
                regra_encontrada = {
                    'id': x[0]
                }
                print('Encontrada regra com id ', regra_encontrada)
                regras.append(regra_encontrada)

        self.mydb.commit()
        return regras


class BuscadorRegras:

    def __init__(self):
        self.database_client = Database()

        self.queue_origem = 'fila_eventos_a_buscar_regras'
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_origem)

        self.channel.basic_consume(self.queue_origem,
                                   self.on_callback_response,
                                   auto_ack=False)

    def testFetch(self):
        json_event = {
            'id': 1,
            'propriedades': {
                'nome': 'Fausto',
                'sobrenome': 'Silva',
                'Departamento': 'Urgencia',
            }
        }

        json_event['regras'] = self.database_client.fetch_regras(json_event)

        print(' [x] buscadas regras para evento com id ', json_event['id'])

    def on_callback_response(self, ch, method, props, body):
        evt_str = body.decode('utf-8')
        print(' [x] obtido ', evt_str)

        # TODO: buscar regras
        json_event = json.loads(evt_str)

        json_event['regras'] = self.database_client.fetch_regras(json_event)

        print(' [x] buscadas regras para evento')
        populated_event = json.dumps(json_event)
        print(' [x] atualizados eventos')

        reply_to_queue = str(props.reply_to)

        self.channel.basic_publish(
            exchange='',
            routing_key=reply_to_queue,
            body=str(populated_event),
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
        )

        # ack no evento da 'fila_eventos_a_buscar_regras'
        ch.basic_ack(delivery_tag=method.delivery_tag)

        print('')
        print(" [.] Aguardando  eventos à processar em", self.queue_origem)

    def consume(self):
        print(" [x] Aguardando  eventos à processar em", self.queue_origem)
        self.channel.start_consuming()


buscador = BuscadorRegras()
buscador.consume()
# buscador.testFetch()

