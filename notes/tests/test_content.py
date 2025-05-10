from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

class TestNotesContent(TestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.notes = Note.objects.create(title='Заголовок', text='Текст', author=self.author)

    def test_note_passed_to_list_view_context(self):
        response = self.client.get(reverse('notes:list'))
        self.assertIn('object_list', response.context)
        self.assertIn(self.notes, response.context['object_list'])

    def test_other_users_note_not_in_user_list(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        other_note = Note.objects.create(title='Заметка другого пользователя', text='Текст', author=other_user)

        response = self.client.get(reverse('notes:list'))
        self.assertNotIn(other_note, response.context['object_list'])

    def test_views_have_form_in_context(self):
        views = [reverse('notes:add'), reverse('notes:edit', args=[self.notes.slug])]
        for url in views:
            response = self.client.get(url)
            self.assertIn('form', response.context)
