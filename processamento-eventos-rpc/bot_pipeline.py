#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pika
import uuid
import json
import mysql.connector


class Database:
    def __init__(self):
        self.mydb = mysql.connector.connect(host="localhost", port=3316,
                                            database='eventos_database',
                                            user="root",
                                            passwd="123456")

    def persist_event(self, corr_id, evt_json):
        print(' [DATABASE] corr_id:', corr_id, 'value:', evt_json)

        descricao = evt_json['descricao']

        query = "INSERT INTO tb_evento(description) VALUES('%s')" % descricao

        mycursor = self.mydb.cursor()

        mycursor.execute(query)

        self.mydb.commit()
        print(' [DATABASE] inserido ID', mycursor.lastrowid)
        evt_json['id'] = mycursor.lastrowid
        return evt_json

    def persist_regras(self, evt_regras):
        mycursor = self.mydb.cursor()
        for regra in evt_regras['regras']:
            id_evento = evt_regras['id']
            id_regra = regra['id']

            query = 'INSERT INTO tb_evento_regra(id_evento, id_regra, fg_processada) ' \
                    'VALUES(%s, %s, %d)' % (id_evento, id_regra, 1)
            mycursor.execute(query)

            print(' [CALLBACK] persistida regra do evento', id_evento, ':', json.dumps(regra))

        self.mydb.commit()


class Pipeline:

    def __init__(self):
        self.queue_origem = 'fila_eventos_a_processar'
        self.queue_destino = 'fila_eventos_a_buscar_regras'

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        print(' [INIT] Inicializada conexão com RabbitMQ')

        self.database_client = Database()
        print(' [INIT] Inicializada conexão com MySQL')

        self.response = None
        self.corr_id = None
        self.delivery_tag = None

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_origem)
        self.channel.queue_declare(queue=self.queue_destino)

        # cria fila de callback exclusivo para BOT, e consumí-lo
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        print(' [INIT] Criada fila', self.callback_queue, ', exclusiva para callback de evento + regras')

        self.channel.basic_consume(self.callback_queue,
                                   self.on_rpc_callback,
                                   auto_ack=False)

        self.channel.basic_qos(prefetch_count=1)

        print(" [INIT] Aguardando callback de eventos em", self.callback_queue)

    def testInsertEvento(self):
        self.database_client.persist_event('corr_id_example', {"descricao": "test"})
        print('inserido evento de teste')

    def testInsertRegras(self):
        evt_regras = {
            'id': 1,
            'regras': [
                {
                    'id': 2
                },
                {
                    'id': 3
                }
            ]
        }
        self.database_client.persist_regras(evt_regras)
        print('inseridas regras no evento')

    # no consumo da fila de callback
    def on_rpc_callback(self, ch, method, props, body):
        print(' [CALLBACK] obtido callback response com corr_id', props.correlation_id)
        if self.corr_id == props.correlation_id:
            self.response = body.decode('utf-8')
            print(' [CALLBACK] obtido response:', self.response)
            # TODO: persistir evento+regras na base de dados
            evt_regras = json.loads(self.response)
            self.database_client.persist_regras(evt_regras)
            print(' [CALLBACK] persistido evento+regras com uuid', self.corr_id)

            # ack no evento da "fila_callback"
            ch.basic_ack(delivery_tag=method.delivery_tag)

            # ack no evento da 'fila_eventos_a_processar'
            self.channel.basic_ack(delivery_tag=self.delivery_tag)

            # print(' [CALLBACK] confirmados eventos')
            print(' --------------------------------------- ')
            print(" [INIT] Aguardando  eventos à processar em", self.queue_origem)
            print()

    # publicar na fila "eventos_a_buscar_regras"
    def send_to_process(self, evt_str):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        print('buscando evt_json')
        print('evt_json', evt_str)

        # print(' [À BUSCAR REGRAS] persistindo evento na base de dados com corr_id', self.corr_id)
        evt_json = self.database_client.persist_event(self.corr_id, json.loads(evt_str))
        evt_str = json.dumps(evt_json)
        print(' [À BUSCAR REGRAS] persistido evento com corr_id', self.corr_id, 'na base de dados: ', evt_str)

        print(' [À BUSCAR REGRAS] publicando evento em', self.queue_destino, 'com corr_id', self.corr_id)
        print()
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_destino,
            body=evt_str,
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

        event = body.decode('utf-8')
        print(' [À BUSCAR REGRAS] obtido evento:', str(event))

        # publicar evento na fila 'eventos_a_buscar_regras', com propriedade de fila de callback criada
        self.send_to_process(event)

    # consumir evento da "fila_eventos_a_processar"
    def consume(self):
        # consumir 'fila_eventos_a_processar'
        self.channel.basic_consume(self.queue_origem,
                                   self.on_regra_recebida,
                                   auto_ack=False)

        self.channel.basic_qos(prefetch_count=1)

        print(" [INIT] Awaiting RPC requests")
        print(" [INIT] Aguardando  eventos à processar em", self.queue_origem)
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
# pipeline.testInsertEvento()
# pipeline.testInsertRegras()

