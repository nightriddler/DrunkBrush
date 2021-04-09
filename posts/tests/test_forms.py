import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post
from yatube.settings import LOGIN_URL

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(
            username='writer',
        )
        cls.user_second = User.objects.create_user(
            username='writer_second',
        )
        cls.group_first = Group.objects.create(
            title='Первая группа',
            slug='test-slug',
        )
        cls.group_second = Group.objects.create(
            title='Вторая',
            slug='test-second',
        )
        cls.post = Post.objects.create(
            text='Первый текст',
            author=cls.user,
            group=cls.group_first,
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

        self.user_second = User.objects.get(username='writer_second')
        self.authorized_client_second = Client()
        self.authorized_client_second.force_login(self.user_second)

    def test_create_new_post_from_forms(self):
        """Проверяем добавления нового поста
        в базу через форму на странице new."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_post = {
            'text': 'Второй текст',
            'group': self.group_second.id,
        }
        form_image = {
            'image': uploaded,
        }
        response_post_guest = self.guest_client.post(
            reverse('new_post'), data=form_post, follow=True)
        self.assertRedirects(
            response_post_guest, f'{LOGIN_URL}?next={reverse("new_post")}')
        self.assertEqual(
            Post.objects.count(),
            post_count,
            'Пост добавлен не авторизованным пользователем'
        )
        response_post_authorized = self.authorized_client.post(
            reverse('new_post'),
            data=form_post,
            file_data=form_image,
            follow=True
        )
        self.assertRedirects(response_post_authorized, reverse('index'))
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            'Не добавляется пост авторизованным пользователем'
        )
        second_post = Post.objects.get(id=2)
        self.assertEqual(
            self.post.author,
            second_post.author,
            'Второй пост добавляется другим пользователем'
        )
        self.assertEqual(
            self.group_second,
            second_post.group,
            'Пост добавлен в другую группу'
        )

    def test_post_edit_from_forms_after_save(self):
        """Проверка сохранения записи, после редактирования поста."""
        form_post = {
            'text': 'Отредактирован',
            'group': self.group_second.id
        }
        responses = [self.guest_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            ),
            data=form_post,
            follow=True
        ), self.authorized_client_second.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            ),
            data=form_post,
            follow=True
        )]
        for response in responses:
            with self.subTest():
                self.assertRedirects(
                    response, f'/{self.user.username}/{self.post.id}/')

        response_authorized = self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            ),
            data=form_post,
            follow=True
        )
        self.assertRedirects(
            response_authorized, f'/{self.user.username}/{self.post.id}/')
        self.post.refresh_from_db()
        self.assertEqual(
            self.post.text,
            form_post['text'],
            'Поле text не изменилось'
        )
        self.assertEqual(
            self.post.group_id,
            form_post['group'],
            'Поле group не измененилось'
        )

        response_page_first_group = self.guest_client.get(
            reverse('page_group', kwargs={'slug': self.group_first.slug}))
        count_post = len(response_page_first_group.context['page'].object_list)
        self.assertEqual(
            0,
            count_post,
            'Пост не пропал при изменении группы'
        )

        response_page_second_group = self.guest_client.get(
            reverse('page_group', kwargs={'slug': self.group_second.slug}))
        count_post = len(
            response_page_second_group.context['page'].object_list)
        self.assertEqual(
            1,
            count_post,
            'Пост не появился на странице измененной группы'
        )

    def test_add_comment_form(self):
        """Проверка комментариев."""
        form_comment = {
            'text': 'Текст комментария',
        }
        count_before_add_comment = Comment.objects.all().count()
        self.guest_client.post(reverse(
            'add_comment',
            kwargs={'username': self.user.username, 'post_id': self.post.id}),
            data=form_comment,
            follow=True
        )
        count_after_add_comment_guest = Comment.objects.all().count()
        self.assertEqual(
            count_before_add_comment,
            count_after_add_comment_guest,
            'Добавляется комментарий не авторизованным пользователем'
        )
        self.authorized_client.post(reverse(
            'add_comment',
            kwargs={'username': self.user.username, 'post_id': self.post.id}),
            data=form_comment,
            follow=True
        )
        count_after_add_comment = Comment.objects.all().count()
        self.assertNotEqual(
            count_before_add_comment,
            count_after_add_comment,
            'Не добавляется комментарий авторизованным пользователем'
        )
