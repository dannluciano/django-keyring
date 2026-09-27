from django.db import connection, models
from django.test import TransactionTestCase

from .fields import KeyringField


class KeyringTestRecord(models.Model):
    first_secret = KeyringField(disgest_field=True)
    second_secret = KeyringField(disgest_field="second_secret_digest")
    optional_secret = KeyringField(null=True, blank=True)

    class Meta:
        app_label = "keyring"


class KeyringFieldTests(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(KeyringTestRecord)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(KeyringTestRecord)
        super().tearDownClass()

    def test_model_has_one_shared_key_id_field(self):
        key_fields = [
            field
            for field in KeyringTestRecord._meta.local_fields
            if field.name == "encrypted_with_key"
        ]

        self.assertEqual(len(key_fields), 1)
        self.assertEqual(
            {
                KeyringTestRecord._meta.get_field("first_secret").cypher_key_field_name,
                KeyringTestRecord._meta.get_field("second_secret").cypher_key_field_name,
            },
            {"encrypted_with_key"},
        )

    def test_descriptor_keeps_model_instance_on_field(self):
        record = KeyringTestRecord(first_secret="classified")
        field = KeyringTestRecord._meta.get_field("first_secret")

        self.assertIs(field.model_instance, record)
        self.assertEqual(record.first_secret, "classified")
        self.assertIs(field.model_instance, record)

    def test_save_stores_ciphertext_shared_key_id_and_digests(self):
        record = KeyringTestRecord.objects.create(
            first_secret="first value",
            second_secret="second value",
        )
        stored_values = KeyringTestRecord.objects.filter(pk=record.pk).values(
            "first_secret",
            "second_secret",
            "encrypted_with_key",
            "first_secret_digest",
            "second_secret_digest",
        ).get()

        self.assertNotEqual(stored_values["first_secret"], "first value")
        self.assertNotEqual(stored_values["second_secret"], "second value")
        self.assertEqual(stored_values["encrypted_with_key"], 2)
        self.assertTrue(stored_values["first_secret_digest"])
        self.assertTrue(stored_values["second_secret_digest"])

    def test_loaded_model_decrypts_every_encrypted_field(self):
        record = KeyringTestRecord.objects.create(
            first_secret="first value",
            second_secret="second value",
        )

        loaded_record = KeyringTestRecord.objects.get(pk=record.pk)

        self.assertEqual(loaded_record.first_secret, "first value")
        self.assertEqual(loaded_record.second_secret, "second value")
        self.assertEqual(loaded_record.encrypted_with_key, 2)

    def test_empty_encrypted_fields_load_without_decryption_error(self):
        record = KeyringTestRecord.objects.create(
            first_secret="",
            second_secret="",
        )

        loaded_record = KeyringTestRecord.objects.get(pk=record.pk)

        self.assertEqual(loaded_record.first_secret, "")
        self.assertEqual(loaded_record.second_secret, "")
        self.assertIsNone(loaded_record.optional_secret)
