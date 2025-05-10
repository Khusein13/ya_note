from django.test import TestCase

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note
from django.contrib.auth.models import User

User = get_user_model()


class TestNotes(TestCase):
    TITLE = 'Заголовок заметки'
    TEXT = 'Тестовый текст'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testUser')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.author = User.objects.create_user(username='testuser', password='testpass')
        cls.notes = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
        )

    def test_successful_creation(self):
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_title(self):
        self.assertEqual(self.notes.title, self.TITLE)
