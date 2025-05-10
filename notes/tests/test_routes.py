from http import HTTPStatus
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаем пользователя и заметку
        cls.author = User.objects.create_user(username='testuser', password='testpass')
        cls.notes = Note.objects.create(title='Заголовок', text='Текст', author=cls.author)

    def setUp(self):
        # Авторизуем пользователя перед каждым тестом
        self.client.login(username='testuser', password='testpass')

    def check_page_accessibility(self, url, expected_status=HTTPStatus.OK):
        response = self.client.get(url)
        self.assertEqual(response.status_code, expected_status)

    def test_pages_accessibility(self):
        urls = [
            reverse('notes:home'),
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
            reverse('notes:detail', args=[self.notes.slug]),
            reverse('notes:edit', args=[self.notes.slug]),
            reverse('notes:delete', args=[self.notes.slug]),
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:logout'),
        ]

        for url in urls:
            with self.subTest(url=url):
                self.check_page_accessibility(url)

    def test_other_user_cannot_access_note_detail(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.client.logout()
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.get(reverse('notes:detail', args=[self.notes.slug]))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        urls = [
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
            reverse('notes:detail', args=[self.notes.slug]),
            reverse('notes:edit', args=[self.notes.slug]),
            reverse('notes:delete', args=[self.notes.slug]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"/auth/login/?next={url}")
