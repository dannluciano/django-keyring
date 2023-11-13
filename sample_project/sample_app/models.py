from django.db import models
from keyring.fields import KeyringField


class Message(models.Model):
    user = KeyringField(disgest_field=True)
    
    text = KeyringField()

    room = KeyringField(disgest_field='room_sha_digest')

    def __str__(self):
        return self.text