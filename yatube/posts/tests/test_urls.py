from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client
from django.test.testcases import TestCase

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='TestUserAuthor')
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.author)
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group_slug'
        )

    def test_common_pages_are_avaliable(self):
        """Общедоступные страницы доступны"""
        common_pages = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.author.username}/',
            f'/posts/{self.post.pk}'
        ]
        for adress in common_pages:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_avaliable_for_authentificated(self):
        """Страница создания поста доступна авторизованному"""
        response = self.authorized_client_author.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_unavaliable_for_guest(self):
        """Страница создания поста недоступна анонимному"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_avaliable_for_author(self):
        """Страница редактирования поста доступна автору"""
        response = self.authorized_client_author.get(
            f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_unavaliable_for_nonauthor(self):
        """Страница редактирования редиректит не автора на страницу поста"""
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/',
            follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.pk}')

    def test_unexisting_page_404(self):
        """Несуществующая страница возвращает 404"""
        response = self.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """Адреса используют корректные шаблоны"""
        templates_urls = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html'
        }
        for adress, template in templates_urls.items():
            with self.subTest(adress=adress):
                response = self.authorized_client_author.get(adress)
                self.assertTemplateUsed(response, template)
