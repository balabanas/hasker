import json

from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.test import TestCase

from tests.basesite.utils import create_test_data
from django.urls import reverse


class FuncViewAcceptAnswerTest(TestCase):
    def setUp(self) -> None:
        ids = create_test_data()
        self.data = {
            'question_id': ids['q1'],
            'answer_id': ids['a1'],
        }
        self.user = User.objects.get(id=ids['u'])

    def test_post_login_required(self):
        response: TemplateResponse = self.client.post(reverse('accept-answer', args=[self.data['question_id'],
                                                                                     self.data['answer_id']]),
                                                      self.data)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Login required', content['result'])

    def test_post_not_found(self):
        self.client.force_login(self.user)
        self.data['question_id'] = 100500
        self.data['answer_id'] = 100500
        response: TemplateResponse = self.client.post(reverse('accept-answer', args=[self.data['question_id'],
                                                                                     self.data['answer_id']]),
                                                      self.data)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Not found', content['result'])

    def test_post_question_user_mismatch(self):
        u, _ = User.objects.get_or_create(username='aa_testuser')  # question created by `testuser1`
        self.client.force_login(u)
        response: TemplateResponse = self.client.post(reverse('accept-answer', args=[self.data['question_id'],
                                                                                     self.data['answer_id']]),
                                                      self.data)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Not found', content['result'])

    def test_post_success(self):
        # create_test_data()
        u = User.objects.get(username='testuser1')
        self.client.force_login(u)
        response: TemplateResponse = self.client.post(reverse('accept-answer', args=[self.data['question_id'],
                                                                                     self.data['answer_id']]),
                                                      self.data)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Success', content['result'])