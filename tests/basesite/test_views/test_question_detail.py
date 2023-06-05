from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from basesite.models import Answer
from tests.basesite.utils import create_test_data


class QuestionDetailViewTest(TestCase):
    def test_not_exists(self):
        response = self.client.get(reverse('question-detail', args='1'))
        self.assertEqual(404, response.status_code)

    def test_get_success(self):
        ids = create_test_data()
        response = self.client.get(reverse('question-detail', args=[ids['q1']]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Q title')
        self.assertTemplateUsed(response, 'basesite/question_detail.html')

    def test_post_answer_forbidden(self):
        ids = create_test_data()
        data = {'message': 'Test answer message'}
        response = self.client.post(reverse('question-detail', args=[ids['q1']]), data)
        self.assertEqual(403, response.status_code)

    def test_post_answer_too_short(self):
        ids = create_test_data()
        self.client.force_login(user=User.objects.get(pk=ids['u']))
        data = {'message': 'shrt'}
        response = self.client.post(reverse('question-detail', args=[ids['q1']]), data)
        self.assertEqual(200, response.status_code)  # request successful, but not answer created: too short

        answers = Answer.objects.filter(message='shrt')
        self.assertEqual(0, answers.count())

    def test_post_answer_success_redirect(self):
        ids = create_test_data()
        self.client.force_login(user=User.objects.get(pk=ids['u']))
        data = {'message': 'Test answer message'}
        response = self.client.post(reverse('question-detail', args=[ids['q1']]), data)
        self.assertEqual(302, response.status_code)  # redirect

        answers = Answer.objects.filter(message='Test answer message')
        self.assertEqual(1, answers.count())
