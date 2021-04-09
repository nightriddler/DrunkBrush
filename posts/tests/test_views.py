import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post
from yatube.settings import PAR_PAGE

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='test-slug',
            description='Тут описание группы'
        )
        cls.user = User.objects.create_user(username='writer')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тут текст сообщения',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='writer')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': reverse('index'),
            'group_list.html': reverse('all_group'),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
            'group.html': (
                reverse('page_group', kwargs={'slug': self.group.slug})
            ),
            'new.html': reverse('new_post'),
            'follow.html': reverse('follow_index'),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_count_page_show_correct(self):
        """Paginator в шаблоне index показывает
        корректное количество постов на странице."""
        Post.objects.bulk_create([Post(
            text=i,
            author=self.user)
            for i in range(PAR_PAGE * 2)])

        response = self.guest_client.get(reverse('index'))
        post = response.context['page']

        count_post_in_page = len(post.object_list)
        self.assertEqual(count_post_in_page, PAR_PAGE)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('index'))
        post_from_context = response.context['page'][0]
        self.assertEqual(self.post.text, post_from_context.text)
        self.assertEqual(self.post.author, post_from_context.author)
        self.assertEqual(self.post.group, post_from_context.group)
        self.assertEqual(self.post.image, post_from_context.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('all_group'))
        self.assertEqual(
            self.group, response.context['total_group'][0])

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом.
        Проверка нового поста на странице выбранной группы."""
        response = self.authorized_client.get(
            reverse('page_group', kwargs={'slug': self.group.slug}))

        post_from_context = response.context['page'][0]
        self.assertEqual(self.post.text, post_from_context.text)
        self.assertEqual(self.post.author, post_from_context.author)
        self.assertEqual(self.post.group, post_from_context.group)
        self.assertEqual(self.post.image, post_from_context.image)
        self.assertEqual(self.group, response.context['group'])

    def test_new_page_show_correct_context(self):
        """Шаблон new для (new_post и post_edit)
        сформирован с правильным контекстом."""
        responses = [
            self.authorized_client.get(reverse('new_post')),
            self.authorized_client.get(
                reverse(
                    'post_edit',
                    kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id
                    }
                )
            )
        ]
        for response in responses:
            with self.subTest():
                post = response.context['form']['text']
                self.assertEqual(post.label, 'Текст сообщения')
                self.assertEqual(post.help_text, 'Введите текст')

            group = response.context['form']['group']
            self.assertEqual(group.label, 'Группа')
            self.assertEqual(group.help_text, 'Укажите группу')

    def test_profile_and_post_page_show_correct_context(self):
        """Шаблоны profile для сформированы с правильны шаблоном."""
        response = self.guest_client.get(reverse(
            'profile', kwargs={'username': self.user.username}))
        post_from_context = response.context['page'][0]
        self.assertEqual(self.post.text, post_from_context.text)
        self.assertEqual(self.post.author, post_from_context.author)
        self.assertEqual(self.post.group, post_from_context.group)
        self.assertEqual(self.post.image, post_from_context.image)
        self.assertEqual(self.user, response.context['author'])
        self.assertEqual(1, response.context['posts'].count())

    def test_profile_and_post_page_show_correct_context(self):
        """Шаблоны post для сформированы с правильны шаблоном."""
        response = self.guest_client.get(
            reverse(
                'post', kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )
        post_from_context = response.context['post']
        self.assertEqual(self.post.text, post_from_context.text)
        self.assertEqual(self.post.author, post_from_context.author)
        self.assertEqual(self.post.group, post_from_context.group)
        self.assertEqual(self.post.image, post_from_context.image)

    def test_initial_new_post_in_index_and_group(self):
        """Отображение нового поста на странице группы,
        другой группы и на главной."""
        second_post = Post.objects.create(
            text='Текст нового сообщения',
            author=self.user,
            group=Group.objects.create(
                title='Другая группа',
                slug='test-second-slug',
            )
        )
        response = self.guest_client.get(
            reverse('page_group', kwargs={'slug': 'test-second-slug'}))
        self.assertEqual(second_post, response.context['page'][0])

        response = self.authorized_client.get(
            reverse('page_group', kwargs={'slug': self.group.slug}))
        self.assertNotEqual(second_post, response.context['page'][0])

        response = self.guest_client.get(reverse('index'))
        self.assertEqual(second_post, response.context['page'][0])

    def test_cahce_index_page(self):
        """Проверка кэша постов в шаблоне index.html."""
        first_response = self.guest_client.get(reverse('index'))
        first_content = first_response.content

        Post.objects.create(
            text='Тут текст сообщения',
            author=self.user
        )
        second_response = self.guest_client.get(reverse('index'))
        second_content = second_response.content
        self.assertEqual(
            first_content,
            second_content,
            'Контент не кэшируется'
        )

    def test_subscribe_authorized_user(self):
        """Проверка подписок."""
        second_user = User.objects.create_user(username='author')
        check_post = Post.objects.create(
            text='Текст автора',
            author=second_user
        )
        Follow.objects.create(user=self.user, author=second_user)

        response_subscribe = self.authorized_client.get(
            reverse('follow_index'))
        post_from_follow_index = response_subscribe.context['page'][0]

        self.assertEqual(
            check_post.text,
            post_from_follow_index.text,
            'Не работает подписка (текст поста не совпадает)'
        )
        self.assertEqual(
            check_post.author,
            post_from_follow_index.author,
            'Не работает подписка (автор поста не совпадает)'
        )

        second_authorized_client = Client()
        second_authorized_client.force_login(second_user)

        response_second_user = second_authorized_client.get(
            reverse('follow_index'))
        count_post_second_user = response_second_user.context[
            'page'].object_list.count()
        self.assertEqual(
            0,
            count_post_second_user,
            'Новый пост виден в ленте не подписанному пользователю'
        )

        follow = Follow.objects.get(user=self.user, author=second_user)
        follow.delete()

        response_delete_subscribe = self.authorized_client.get(reverse(
            'follow_index'))
        count_post_follow_index = len(
            response_delete_subscribe.context['page'])
        self.assertEqual(
            0,
            count_post_follow_index,
            'Не работает отписка(пост в ленте)'
        )

    def test_comment(self):
        """Проверка комментариев."""
        count_before_add_comment = Comment.objects.all().count()
        Comment.objects.create(
            text='Текст комментария',
            post=self.post,
            author=self.user,
        )
        count_after_add_comment = Comment.objects.all().count()
        self.assertNotEqual(
            count_before_add_comment,
            count_after_add_comment,
            'Комментарий не добавляется авторизованным пользователем')
