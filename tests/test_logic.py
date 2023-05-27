from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    # Текст комментария понадобится в нескольких местах кода, 
    # поэтому запишем его в атрибуты класса.
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.anonimous = Client()
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        #cls.note_id = 'note.id'
        #cls.note = Note.objects.create(
           # title='Заголовок',
           # text='Текст',
           # slug='slug_id',
           # author=cls.author
        #)
        # Адрес страницы с новостью.
        #cls.url = reverse('notes:detail', args=(self.note.id,))
        # Создаём пользователя и клиент, логинимся в клиенте.
        #cls.user = User.objects.create(username='Мимо Крокодил')

        # Данные для POST-запроса при создании комментария.
        #cls.form_data = {'text': cls.COMMENT_TEXT}

    def test_anonymous_user_cant_create_note(self):
        # Считаем количество комментариев.
        note_count = Note.objects.count()
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug_id',
            author=self.author
        )
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом комментария.
        self.client.post(self.url, data=self.form_data)

        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        self.assertEqual(note_count, 0)

    def test_user_can_create_note(self):
        # Совершаем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что редирект привёл к разделу с комментами.
        self.assertRedirects(response, f'{self.url}#notes')
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть один комментарий.
        self.assertEqual(notes_count, 1)
        # Получаем объект комментария из базы.
        note = Note.objects.get()
        # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.slug)
        self.assertEqual(note.author, self.author)


class TestNoteEditDelete(TestCase):
    # Тексты для комментариев не нужно дополнительно создавать
    # (в отличие от объектов в БД), им не нужны ссылки на self или cls,
    # поэтому их можно перечислить просто в атрибутах класса.
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённая заметка'

    @classmethod
    def setUpTestData(cls):
        # Создаём новость в БД.
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        # Сохраняем id новости во временную переменную: так удобнее.# slug='slug_id',
        note_id = cls.note.id
        # Формируем адреса, которые понадобятся для тестов.
        cls.url = reverse('notes:detail', args=(note_id,))  # Адрес новости.
        #cls.url_to_comments = cls.url + '#comments'  # Адрес блока с комментариями.
        cls.edit_url = reverse('notes:edit', args=(note_id,))  # URL для редактирования.
        cls.delete_url = reverse('notes:delete', args=(note_id,))  # URL для удаления.
        # Создаём пользователя - автора комментария.
        cls.author = User.objects.create(username='Автор')
        # Создаём клиент для пользователя-автора.
        cls.author_client = Client()
        # "Логиним" пользователя в клиенте.
        cls.author_client.force_login(cls.author)
        # Делаем всё то же самое для пользователя-читателя.
        #cls.reader = User.objects.create(username='Читатель')
        #cls.reader_client = Client()
        #cls.reader_client.force_login(cls.reader)
        # Создаём объект комментария.
        #cls.comment = Note.objects.create(
            #news=cls.news,
            #author=cls.author,
            #text=cls.COMMENT_TEXT
        #)
        # Формируем данные для POST-запроса по обновлению комментария.
        cls.form_data = {'text': cls.NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к разделу с комментариями.
        # Заодно проверим статус-коды ответов.
        self.assertRedirects(response, self.url)
        # Считаем количество комментариев в системе.
        notes_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(notes_count, 0)

    def test_author_can_edit_note(self):
        # Выполняем запрос на редактирование от имени автора комментария.
        response = self.author_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.url)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст комментария соответствует обновленному.
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
