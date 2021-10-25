from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post

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
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user
        )

    def test_create_post(self):
        """Валидная форма создает запись Post"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост2'
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост2'
            ).exists()
        )

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
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            form_data['text'],
            Post.objects.get(pk=self.post.pk).text
        )
