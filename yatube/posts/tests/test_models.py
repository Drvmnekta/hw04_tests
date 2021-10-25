from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_posts_have_correct_object_names(self):
        """Проверка, что у поста корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(post.__str__(), post.text[:15])

    def test_groups_have_correct_object_names(self):
        """Проверка, что у группы корректно работает __str__."""
        group = PostModelTest.group
        self.assertEqual(group.__str__(), group.title)

    def test_verboses(self):
        """Проверка, что у полей корректно работают verbose_name"""
        post = PostModelTest.post
        verboses = {
            'text': 'Текст поста',
            'group': 'Группа',
            'pub_date': 'Дата публикации',
            'author': 'Автор'
        }
        for field, expected_value in verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_texts(self):
        """Проверка, что у полей корректно работают help_text"""
        post = PostModelTest.post
        helps = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу'
        }
        for field, expected_value in helps.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
