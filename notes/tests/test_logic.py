from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from notes.models import Note
from pytils.translit import slugify


class NoteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.anonymous_user = User.objects.create_user(username='anonuser', password='anonpass')

    def test_logged_in_user_can_create_note(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('notes:add'), data={
            'title': 'Test Note',
            'text': 'This is a test note.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.get().title, 'Test Note')

    def test_anonymous_user_cannot_create_note(self):
        response = self.client.post(reverse('notes:add'), data={
            'title': 'Test Note',
            'text': 'This is a test note.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 0)

    def test_duplicate_slug_not_allowed(self):
        self.client.login(username='testuser', password='testpass')
        Note.objects.create(title='Note 1', text='Content 1', slug='unique-slug', author=self.user)
        response = self.client.post(reverse('notes:add'), data={
            'title': 'Note 2',
            'text': 'Content 2',
            'slug': 'unique-slug',
        })
        self.assertEqual(response.status_code, 200)

    def test_auto_slug_generation(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('notes:add'), data={
            'title': 'Test Note Without Slug',
            'text': 'This is a test note without slug.',
        })
        note = Note.objects.get(title='Test Note Without Slug')
        self.assertEqual(note.slug, slugify('Test Note Without Slug'))

    def test_user_can_edit_own_note(self):
        self.client.login(username='testuser', password='testpass')
        note = Note.objects.create(title='Own Note', text='Some content.', author=self.user)
        response = self.client.post(reverse('notes:edit', kwargs={'slug': note.slug}), data={
            'title': 'Updated Note',
            'text': 'Updated content.',
        })
        self.assertEqual(response.status_code, 302)
        note.refresh_from_db()
        self.assertEqual(note.title, 'Updated Note')

    def test_user_cannot_edit_others_note(self):
        self.client.login(username='testuser', password='testpass')
        other_user_note = Note.objects.create(title='Other Note', text='Content.', author=self.anonymous_user)
        response = self.client.post(reverse('notes:edit', kwargs={'slug': other_user_note.slug}), data={
            'title': 'Hacker Note',
            'text': 'Hacker content.',
        })
        self.assertEqual(response.status_code, 404)

    def test_user_can_delete_own_note(self):
        self.client.login(username='testuser', password='testpass')
        note = Note.objects.create(title='Deletable Note', text='Content.', author=self.user)
        response = self.client.post(reverse('notes:delete', kwargs={'slug': note.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(id=note.id).exists())

    def test_user_cannot_delete_others_note(self):
        self.client.login(username='testuser', password='testpass')
        other_user_note = Note.objects.create(title='Other Deletable Note', text='Content.', author=self.anonymous_user)
        response = self.client.post(reverse('notes:delete', kwargs={'slug': other_user_note.slug}))
        self.assertEqual(response.status_code, 404)
