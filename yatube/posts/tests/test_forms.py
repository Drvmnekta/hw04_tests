from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUPClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user
        )
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug'
        )

    def test_create_post(self):
        """Валидная форма создает запись Post"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост2',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text']
            ).exists()
        )
        created_post = Post.objects.get(text=form_data['text'])
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.group.pk, form_data['group'])
        self.assertEqual(created_post.author, self.user)

    def test_edit_post(self):
        """Валидная форма меняет содержание записи, не дублируя ее"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный тестовый пост'
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            form_data['text'],
            Post.objects.get(pk=self.post.pk).text
        )

    def test_guest_client_cant_create_post(self):
        form_data = {
            'text': 'Тестовый пост2',
            'group': self.group
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        reverse_login = reverse('users:login')
        reverse_create = reverse('posts:post_create')
        self.assertRedirects(
            response, f'{reverse_login}?next={reverse_create}')

    def test_guest_client_cant_edit_post(self):
        form_data = {
            'text': 'Измененный тестовый пост'
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
