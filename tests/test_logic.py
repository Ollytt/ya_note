from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.anonimous = Client()
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': 'slug_id'
        }
        cls.add_url = reverse('notes:add')

    def test_anonymous_user_cant_create_note(self):
        note_count = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(note_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(
            self.add_url,
            data=self.form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённая заметка'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='slug_id',
            author=cls.author
        )
        note_id = cls.note.slug
        cls.url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(note_id,))
        cls.delete_url = reverse('notes:delete', args=(note_id,))
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Обновлённая заметка',
            'slug': 'slug_id'
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
