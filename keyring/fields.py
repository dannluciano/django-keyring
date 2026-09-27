from django.conf import settings
from django.db import models
from django.db.models import signals
from django.db.models.query_utils import DeferredAttribute
from keyringpy import Keyring

keys = settings.KEYRINGPY_KEYS
salt = settings.KEYRINGPY_SALT
encryptor = Keyring(keys, {"digest_salt": salt})


class KeyringDescriptor(DeferredAttribute):
    def __get__(self, instance, cls=None):
        if instance is not None:
            self.field.model_instance = instance
        return super().__get__(instance, cls)

    def __set__(self, instance, value):
        self.field.model_instance = instance
        instance.__dict__[self.field.attname] = value


class KeyringField(models.TextField):
    description = "TextField encrypted with Keyring"
    descriptor_class = KeyringDescriptor
    cypher_key_field_name = "encrypted_with_key"

    def __init__(self, disgest_field=None, *args, **kwargs):
        self.digest_field = disgest_field
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, private_only=False, **kwargs):
        cls._meta.has_keyring_field = True

        if (
            not any(
                field.name == self.cypher_key_field_name
                for field in cls._meta.local_fields
            )
            and cls.__module__ != "__fake__"
        ):
            cypher_key_field = models.IntegerField(editable=False, null=True)
            cls.add_to_class(self.cypher_key_field_name, cypher_key_field)
            self._cypher_key_field = cypher_key_field

        if self.digest_field:
            self.digest_field_name = f"{name}_digest"
            if isinstance(self.digest_field, str):
                self.digest_field_name = self.digest_field
            digest_field = models.TextField(editable=False, null=True)
            cls.add_to_class(self.digest_field_name, digest_field)

        signals.post_init.connect(self.decrypt, sender=cls, dispatch_uid="_keyring_")
        super().contribute_to_class(cls, name, private_only, **kwargs)

    def decrypt(self, instance, force=False, *args, **kwargs):
        if instance.pk and not hasattr(instance, "_decrypted"):
            fields = instance._meta.get_fields()
            cypher_key = getattr(instance, self.cypher_key_field_name)
            for field in fields:
                if isinstance(field, KeyringField):
                    cypher_text = getattr(instance, field.attname)
                    if cypher_text:
                        plain_text = encryptor.decrypt(cypher_text, cypher_key)
                        setattr(instance, field.attname, plain_text)
            instance._decrypted = True

    def pre_save(self, model_instance, add):
        self.model_instance = model_instance
        plain_text = super().pre_save(model_instance, add)
        if plain_text:
            cypher_text, keyringId, digest = encryptor.encrypt(plain_text)
            if self.digest_field:
                setattr(model_instance, self.digest_field_name, digest)
            setattr(model_instance, self.cypher_key_field_name, keyringId)
            return cypher_text
        return plain_text
