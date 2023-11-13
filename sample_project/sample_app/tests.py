from django.test import TestCase

from .models import Message


class MessageTestCase(TestCase):
    def setUp(self):
        Message.objects.create(
            user = 'dannluciano',
            text = 'Hello World',
            room = 'irc'
        )

    def test_encrypt_and_decrypt(self):
        message = Message.objects.first()

        self.assertEqual(message.user, 'dannluciano')
        self.assertEqual(message.text, 'Hello World')
        self.assertEqual(message.room, 'irc')

    def test_existence_and_value_of_generated_fields_of_user(self):
        message = Message.objects.first()

        self.assertTrue(hasattr(message, 'user_encrypted_with_key'))
        self.assertEqual(message.user_encrypted_with_key, 2)

        self.assertTrue(hasattr(message, 'user_digest'))
        self.assertEqual(message.user_digest, '2b248a5decf84d3ea324933412f0b2fab4e498dd')

    def test_existence_and_value_of_generated_fields_of_text(self):
        message = Message.objects.first()

        self.assertTrue(hasattr(message, 'text_encrypted_with_key'))
        self.assertEqual(message.text_encrypted_with_key, 2)   

    def test_existence_and_value_of_generated_fields_of_room(self):
        message = Message.objects.first()

        self.assertTrue(hasattr(message, 'room_encrypted_with_key'))
        self.assertEqual(message.user_encrypted_with_key, 2)

        self.assertTrue(hasattr(message, 'room_sha_digest'))
        self.assertEqual(message.room_sha_digest, 'cef4523d1ec94268969ac9c14fa8341e2ecfb678')