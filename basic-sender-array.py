import pika
import time

# A cada 10 segundos:
# Abre conexão com o RabbitMQ
# Declara uma queue
# Para cada nome em um array:
# 1. mona uma mensagem
# 2. publica uma mensagem na queue
# 3. printa na tela
# Encerra a conexão
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
