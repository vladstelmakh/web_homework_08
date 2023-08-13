import pika
import mongoengine
from contact_model import Contact

# Підключення до бази даних MongoDB
db_name = 'my_db1'
db_host = 'localhost'
db_port = 27017

mongoengine.connect(db_name, host=db_host, port=db_port)

# Налаштування з'єднання з RabbitMQ
rabbitmq_host = 'localhost'
queue_name = 'contact_queue'

# З'єднання з RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=queue_name)

def process_contact(contact_id):
    try:
        contact = Contact.objects.get(id=contact_id)
    except Contact.DoesNotExist:
        print(f'Контакт з ID {contact_id} не знайдений.')
        return

    if contact.preferred_method == 'email':
        # Код для відправки електронного листа (функція-заглушка)
        print(f'Відправляємо email на адресу {contact.email}...')
    elif contact.preferred_method == 'sms':
        # Код для відправки SMS (функція-заглушка)
        print(f'Відправляємо SMS на номер {contact.phone_number}...')

    # Встановлюємо поле message_sent в True
    contact.message_sent = True
    contact.save()

def callback(ch, method, properties, body):
    contact_id = body.decode('utf-8')
    process_contact(contact_id)
    print(f'Контакт {contact_id} оброблено.')

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print('Скрипт consumer.py очікує на повідомлення з черги...')
channel.start_consuming()
