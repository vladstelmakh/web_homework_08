from mongoengine import Document, StringField, BooleanField

class Contact(Document):
    full_name = StringField(required=True)
    email = StringField(required=True)
    phone_number = StringField()
    preferred_method = StringField(choices=['email', 'sms'], default='email')
    message_sent = BooleanField(default=False)
