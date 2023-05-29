from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from basesite.models import Question


class QuestionCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_get_login_required_redirect(self):
        response = self.client.get(reverse('create'))
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('create')}")

    def test_get_logged(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('create'))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'basesite/question_form.html')

    def test_post_success(self):
        self.client.force_login(self.user)
        create_data = {
            'title': 'Question title',
            'message': 'Question message',
            'tags': ['a' * i for i in range(1, Question.max_tags + 1)]
        }
        response = self.client.post(reverse('create'), create_data)
        self.assertEqual(302, response.status_code)

    def test_post_validaton_errors(self):
        self.client.force_login(self.user)
        create_data = {
            'title': 'Question title',
            'message': 'Question message',
            'tags': ['a' * i for i in range(1, Question.max_tags + 2)]
        }
        response = self.client.post(reverse('create'), create_data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Maximum number of tags')
