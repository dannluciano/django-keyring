from django.test import TestCase

from .models import Message


class MessageKeyringTests(TestCase):
    def create_message(self, **values):
        defaults = {"user": "dannluciano", "text": "Hello World", "room": "irc"}
        defaults.update(values)
        return Message.objects.create(**defaults)

    def test_message_values_round_trip_through_database(self):
        message = self.create_message()

        loaded_message = Message.objects.get(pk=message.pk)

        self.assertEqual(loaded_message.user, "dannluciano")
        self.assertEqual(loaded_message.text, "Hello World")
        self.assertEqual(loaded_message.room, "irc")

    def test_database_stores_ciphertext_and_one_shared_key_id(self):
        message = self.create_message()

        stored_values = Message.objects.filter(pk=message.pk).values(
            "user",
            "text",
            "room",
            "encrypted_with_key",
        ).get()

        self.assertNotEqual(stored_values["user"], "dannluciano")
        self.assertNotEqual(stored_values["text"], "Hello World")
        self.assertNotEqual(stored_values["room"], "irc")
        self.assertEqual(stored_values["encrypted_with_key"], 2)

        key_id_fields = [
            field
            for field in Message._meta.local_fields
            if field.name == "encrypted_with_key"
        ]
        self.assertEqual(len(key_id_fields), 1)

    def test_generated_digests_are_saved(self):
        message = self.create_message()

        self.assertEqual(message.user_digest, "2b248a5decf84d3ea324933412f0b2fab4e498dd")
        self.assertEqual(message.room_sha_digest, "cef4523d1ec94268969ac9c14fa8341e2ecfb678")

    def test_string_representation_uses_decrypted_text(self):
        message = self.create_message()

        loaded_message = Message.objects.get(pk=message.pk)

        self.assertEqual(str(loaded_message), "Hello World")

    def test_empty_values_can_be_saved_and_loaded(self):
        message = self.create_message(user="", text="", room="")

        loaded_message = Message.objects.get(pk=message.pk)

        self.assertEqual(loaded_message.user, "")
        self.assertEqual(loaded_message.text, "")
        self.assertEqual(loaded_message.room, "")
