import pika
import time

while True:
    # Definindo connection
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    # Opening connection channel
    channel = connection.channel()

    queue_name = 'hello'
    # Declaring queue
    channel.queue_declare(queue=queue_name)

    nomes = ['Araújo', 'Tatiana', 'Valdelice', 'Adenauer', 'Alinne', 'Emerson']
    for nome in nomes:
        message = 'Olá ' + nome + '!'
        # Publishing message to declared queue
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=message)
        print(" [x] Enviado '", message, "'")

    # Closing connection
    connection.close()

    print("Waiting 10 seconds before execute again")
    time.sleep(10)
