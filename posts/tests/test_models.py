from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Writer')
        cls.group = Group.objects.create(title='Заголовок группы')
        cls.post = Post.objects.create(
            text='Тут текст сообщения',
            author=cls.user,
            group=cls.group
        )

    def test_verbose_name(self):
        """Проверка поля verbose_name."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст сообщения',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_text_help_text(self):
        """Проверка поля help_text."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Введите текст',
            'group': 'Укажите группу',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_text_field(self):
        """Отображение поля __str__ и post.text[:15]."""
        post = PostModelTest.post
        field_verboses = {
            post.__str__(): 'Тут текст сообщ',
            post.group.__str__(): 'Заголовок группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value, expected)
