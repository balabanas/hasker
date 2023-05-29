from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import smart_str

from tests.basesite.utils import create_test_data


class HaskerLoginViewTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Log In')
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_post_validation(self):
        create_test_data()
        login_data = {
            'username': 'testuser1',
            'password': 'QWEr4$31_',  # incorrect password
        }
        response: TemplateResponse = self.client.post(reverse('login'), login_data)
        self.assertEqual(200, response.status_code)
        self.assertIn("Please enter a correct username and password", smart_str(response.content))
        login_data['password'] = 'QWEr4$31'
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('list'))
