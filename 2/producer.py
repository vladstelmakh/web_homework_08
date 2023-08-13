import json
import pika
import mongoengine
from faker import Faker
from contact_model import Contact

# Підключення до бази даних MongoDB
db_name = 'my_db1'
db_host = 'localhost'
db_port = 27017

mongoengine.connect(db_name, host=db_host, port=db_port)

fake = Faker()

# Налаштування з'єднання з RabbitMQ
rabbitmq_host = 'localhost'
queue_name = 'contact_queue'

# З'єднання з RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=queue_name)

def generate_fake_contacts(num_contacts):
    contact_ids = []
    for _ in range(num_contacts):
        contact_data = {
            'full_name': fake.name(),
            'email': fake.email(),
            'phone_number': fake.phone_number(),
            'preferred_method': fake.random_element(elements=['email', 'sms']),
        }
        contact = Contact(**contact_data)
        contact.save()
        contact_ids.append(str(contact.id))  # Конвертуємо ObjectId в рядок

    return contact_ids

def send_contacts_to_queue(contact_ids):
    for contact_id in contact_ids:
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=contact_id)

    print(f'{len(contact_ids)} контактів надіслано до черги.')

if __name__ == "__main__":
    num_fake_contacts = 5  # Змініть це на бажану кількість фейкових контактів
    fake_contact_ids = generate_fake_contacts(num_fake_contacts)
    send_contacts_to_queue(fake_contact_ids)

connection.close()
