from django.test import Client
from django.test.testcases import TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_urls_use_correct_templates(self):
        templates_urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for adress, template in templates_urls.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
