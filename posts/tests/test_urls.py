from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='test-slug'
        )
        cls.user = User.objects.create_user(username='writer')
        cls.post = Post.objects.create(
            text='Тут текст сообщения',
            author=cls.user,
            group=cls.group
        )
        cls.second_user = User.objects.create_user(username='another_writer')
        cls.second_post = Post.objects.create(
            text='Тут текст второго сообщения',
            author=cls.second_user
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='writer')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_all_url_exists_at_desired_location(self):
        """URL доступны неавторизованному пользователю
        и имеют соотвествующий шаблон."""
        url_template = {
            '/': 'index.html',
            '/group/': 'group_list.html',
            f'/group/{self.group.slug}/': 'group.html',
            f'/{self.user.username}/': 'profile.html',
            f'/{self.user.username}/{self.post.id}/': 'post.html',
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url in url_template:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

        for reverse_name, template in url_template.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        url_redirect = {
            f'/{self.user.username}/{self.post.id}/edit/': 302,
            '/new/': 302,
        }
        for url, code in url_redirect.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, code)
        url_errors = {
            '/exist_404_page/': 404,
        }
        for url, code in url_errors.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_all_url_exists_at_desired_location_authorized(self):
        """URL доступны авторизованному пользователю
        и имеют соотвествующий шаблон."""
        url_names = {
            '/new/': 'new.html',
            f'/{self.user.username}/{self.post.id}/edit/': 'new.html',
        }
        for url in url_names:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

        for reverse_name, template in url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_url_exists_at_desired_location_authorized_and_author_post(self):
        """Проверка авторизованного пользователя - не автора поста."""
        url_names = {
            f'/{self.second_user.username}/{self.second_post.id}/edit/': 302,
        }
        for url, code in url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, code)
