from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug_id',
            author=cls.author
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        # Через _meta обращаемся к полям модели Note
        # и сравниваем их значение с ожидаемым
        cls.title_field = cls.note._meta.get_field('title')
        cls.slug_field = cls.note._meta.get_field('slug')

    def test_title_max_length(self):
        title_max_length = getattr(self.title_field, 'max_length')
        self.assertEqual(title_max_length, 100)

    def test_slug_max_length(self):
        slug_max_length = getattr(self.slug_field, 'max_length')
        self.assertEqual(slug_max_length, 100)

    def test_slug_unique(self):
        slug_unique = getattr(self.slug_field, 'unique')
        self.assertTrue(slug_unique)


