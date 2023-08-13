import json
from datetime import datetime
from mongoengine import connect, Document, StringField, DateTimeField, ReferenceField, ListField
import redis

# Подключение к облачной базе данных MongoDB Atlas
MONGO_URI = "mongodb://localhost:27017/my_db"
connect(host=MONGO_URI)

# Подключение к Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Модели коллекций
class Author(Document):
    name = StringField(required=True, max_length=100)
    date_of_birth = DateTimeField()
    place_of_birth = StringField()
    biography = StringField()

class Quote(Document):
    author = ReferenceField(Author, reverse_delete_rule=2)
    text = StringField(required=True)
    tags = ListField(StringField())

def load_authors_from_json(file_path):
    with open(file_path, 'r') as file:
        authors_data = json.load(file)

    for author_data in authors_data:
        author = Author(
            name=author_data['fullname'],
            date_of_birth=datetime.strptime(author_data['born_date'], '%B %d, %Y'),
            place_of_birth=author_data['born_location'],
            biography=author_data['description']
        )
        author.save()

def load_quotes_from_json(file_path):
    with open(file_path, 'r') as file:
        quotes_data = json.load(file)

    for quote_data in quotes_data:
        authors = Author.objects(name=quote_data['author'])
        if not authors:
            continue

        author = authors[0]  # Выбираем первого автора из списка

        quote = Quote(
            author=author,
            text=quote_data['quote'],
            tags=quote_data['tags']
        )
        quote.save()


def search_quotes(query):
    # Проверяем, есть ли результат запроса в Redis (кеширование)
    cached_result = redis_client.get(query)
    if cached_result:
        return cached_result.decode('utf-8')

    if query.startswith("name:") or query.startswith("tag:"):
        _, value = query.split(":")
        value = value.strip()

        if query.startswith("name:"):
            # Добавляем поддержку сокращенной записи name:st
            if len(value) <= 2:
                value = f".*{value}.*"
            quotes = Quote.objects(author__name__iregex=value).limit(10)
        elif query.startswith("tag:"):
            # Добавляем поддержку сокращенной записи tag:li
            if len(value) <= 2:
                value = f".*{value}.*"
            quotes = Quote.objects(tags__iregex=value).limit(10)

        result = "\n".join([quote.text for quote in quotes])
    elif query.startswith("tags:"):
        _, tags = query.split(":")
        tags = tags.strip().split(",")
        quotes = Quote.objects(tags__in=tags).limit(10)
        result = "\n".join([quote.text for quote in quotes])
    else:
        result = "Invalid query."

    # Кешируем результат запроса в Redis на 10 минут
    redis_client.setex(query, 600, result)
    return result

if __name__ == "__main__":
    # Загрузка данных в базу данных
    load_authors_from_json("authors.json")
    load_quotes_from_json("quotes.json")

    # Вход в интерактивный режим поиска цитат
    while True:
        user_input = input("Введите команду: ")

        if user_input == "exit":
            break

        result = search_quotes(user_input)
        print(result)
