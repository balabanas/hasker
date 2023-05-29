from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import smart_str


class SignUpViewTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse('sign-up'))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Sign Up')
        self.assertTemplateUsed(response, 'auth/user_form.html')

    def test_post_validation(self):
        signup_data = {
            'username': 'testuser',
            'email': 'testuser@t.com',
            'password1': 'PWQWwe#1',
            'password2': 'PQWwe#1',  # pwd mismatch
        }
        response: TemplateResponse = self.client.post(reverse('sign-up'), signup_data)
        self.assertEqual(200, response.status_code)
        self.assertIn("didn’t match", smart_str(response.content))
        signup_data['password2'] = signup_data['password1']
        response = self.client.post(reverse('sign-up'), signup_data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('list'))