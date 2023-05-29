import json

from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse

from tests.basesite.utils import create_test_data


class FuncViewVoteTest(TestCase):
    def setUp(self) -> None:
        ids = create_test_data()
        self.data_q = {
            'instance_type': 'q',
            'instance_id': ids['q1'],
            'increment': 1,
        }
        self.data_a = {
            'instance_type': 'a',
            'instance_id': ids['a1'],
            'increment': -1,
        }
        self.user = User.objects.get(id=ids['u'])

    def test_post_login_required(self):
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_q['instance_id']]),
                                                      self.data_q)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Login required', content['result'])

    def test_post_wrong_data(self):
        self.client.force_login(self.user)
        self.data_q['increment'] = 2  # invalid increment
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_q['instance_id']]),
                                                      self.data_q)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Wrong request data', content['result'])

    def test_post_q_does_not_exist(self):
        self.client.force_login(self.user)
        self.data_q['instance_id'] = 100500
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_q['instance_id']]),
                                                      self.data_q)  # question does not exist
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Wrong request data', content['result'])

    def test_post_a_does_not_exist(self):
        self.client.force_login(self.user)
        self.data_a['instance_id'] = 100500
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_a['instance_id']]),
                                                      self.data_a)  # answe does not exist
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Wrong request data', content['result'])

    def test_post_q_upvote(self):
        self.client.force_login(self.user)
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_q['instance_id']]),
                                                      self.data_q)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Success', content['result'])
        # repeated attempt to upvote
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_q['instance_id']]),
                                                      self.data_q)
        content = json.loads(response.content)
        self.assertEqual('Already voted', content['result'])

    def test_post_a_downvote_upvote(self):
        self.client.force_login(self.user)
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_a['instance_id']]),
                                                      self.data_a)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Success', content['result'])  # downvoted
        # now, upvote
        self.data_a['increment'] = 1
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_a['instance_id']]),
                                                      self.data_a)
        content = json.loads(response.content)
        self.assertEqual('Success', content['result'])
        # upvote once again
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_a['instance_id']]),
                                                      self.data_a)
        content = json.loads(response.content)
        self.assertEqual('Success', content['result'])
        # and again ... now it is not possible
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_a['instance_id']]),
                                                      self.data_a)
        content = json.loads(response.content)
        self.assertEqual('Already voted', content['result'])
