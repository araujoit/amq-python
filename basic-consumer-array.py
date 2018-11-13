import pika


# Callback function
def callback(ch, method, properties, body):
    print(" [x] Recebido %r" % body)


# Definindo connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# Opening connection channel
channel = connection.channel()

queue_name = 'hello'
# Declaring queue
channel.queue_declare(queue=queue_name)
# Defining consumer function, queue and authomatic ack
channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

print(' [*] Aguardando por mensagens. Para sair digite CTRL+C')
channel.start_consuming()
