#!/usr/bin/env python
import pika


def repeat_to_length(string_to_expand, length):
    return (string_to_expand * (int(length / len(string_to_expand)) + 1))[:length]


nomes = ['Araújo', 'Tatiana', 'Valdelice', 'Adenauer', 'Alinne', 'Emerson']
for nome in nomes:
    message = 'Olá ' + nome + '!' + repeat_to_length('.', len(nome))

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Persiste a declaraçao da fila no disco
    channel.queue_declare(queue='task_queue', durable=True)

    channel.basic_publish(exchange='',
                          routing_key='task_queue',
                          body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # faz a mensagem ser persistida no disco
                          ))
    print(" [x] Enviada msg %r" % message)
    connection.close()
else:
    print("Todos os nomes foram enviados com sucesso.")
