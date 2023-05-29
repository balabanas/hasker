import base64
from datetime import datetime
from urllib.parse import urlparse

from django.urls import reverse, exceptions
from rest_framework import status
from rest_framework.test import APITestCase

from tests.basesite.utils import create_test_data, get_logged_user


class TestQuestionViewSet(APITestCase):
    def setUp(self) -> None:
        get_logged_user(self.client)

    def test_invalid_url(self):
        url = reverse('api-question-detail', args=(0,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        with self.assertRaises(exceptions.NoReverseMatch):
            reverse('api-question-detail', args=('not_a_number', 'another_arg',))

    def test_unauthenticated(self):
        self.client.logout()
        url = reverse('api-question-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual({'detail'}, set(response.data.keys()))

    def test_basic_authentication(self):
        self.client.logout()
        create_test_data()
        url = reverse('api-question-list')
        auth = ('testuser1', '_QWEr4$31')  # wrong pwd
        response = self.client.get(url, **{'HTTP-ACCEPT': 'application/json',
                                           'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(
                                               ':'.join(auth).encode()).decode()})
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

        auth = ('testuser1', 'QWEr4$31')
        response = self.client.get(url, **{'HTTP-ACCEPT': 'application/json',
                                           'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(
                                               ':'.join(auth).encode()).decode()})

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_empty_response_ok(self):
        url = reverse('api-question-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_fields_expected(self):
        url = reverse('api-question-list')
        response = self.client.get(url)
        fields_expected = ['count', 'next', 'previous', 'results', 'page_count']
        self.assertEqual(set(fields_expected), set(response.data.keys()))

    def test_return_model_fields_expected(self):
        ids = create_test_data()
        url = reverse('api-question-list')
        response = self.client.get(url)
        fields_expected = ['author', 'title', 'message', 'date_created', 'votes', 'url', 'has_tags', 'tags_url',
                           'has_answers', 'answers_url']
        self.assertEqual(set(fields_expected), set(response.data['results'][0].keys()))

    def test_return_questions_in_one_page(self):
        create_test_data()
        url = reverse('api-question-list')
        response = self.client.get(url)
        self.assertEqual(3, len(response.data['results']))
        self.assertEqual(1, response.data['page_count'])

    def test_change_ordering(self):
        create_test_data()
        url = reverse('api-question-list')  # default ordering: -date_created
        response = self.client.get(url)
        dates = [datetime.strptime(q['date_created'], '%Y-%m-%dT%H:%M:%S.%fZ') for q in response.data['results']]
        self.assertEqual(sorted(dates, reverse=True), dates)
        url = reverse('api-question-list') + '?ordering=date_created'
        response = self.client.get(url)
        dates = [datetime.strptime(q['date_created'], '%Y-%m-%dT%H:%M:%S.%fZ') for q in response.data['results']]
        self.assertEqual(sorted(dates), dates)

    def test_retrieve_question_not_exist(self):
        url = reverse('api-question-detail', args=(0,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual({'detail'}, set(response.data.keys()))

    def test_retrieve_question(self):
        ids = create_test_data()
        url = reverse('api-question-detail', args=(ids['q1'],))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('testuser1', response.data['author'])

    def test_correct_ulrs_returned(self):
        ids = create_test_data()
        url = reverse('api-question-detail', args=(ids['q1'],))
        response = self.client.get(url)
        url_path = urlparse(response.data['url']).path
        tags_url_path = urlparse(response.data['tags_url']).path
        answers_url_path = urlparse(response.data['answers_url']).path
        self.assertEqual(f'/api/v1/questions/{ids["q1"]}/', url_path)
        self.assertEqual(f'/api/v1/questions/{ids["q1"]}/tags/', tags_url_path)
        self.assertEqual(f'/api/v1/questions/{ids["q1"]}/answers/', answers_url_path)

    def test_list_trending_questions_empty(self):
        url = reverse('api-question-trending-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search(self):
        create_test_data()
        url = reverse('api-question-list') + '?search=Q3'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        url = reverse('api-question-list') + '?search=A to Q2'  # search in Answer's content
        response = self.client.get(url)
        self.assertEqual(1, len(response.data['results']))
        url = reverse('api-question-list') + '?search=NotExisting A to Q2'  # search in Answer's content
        response = self.client.get(url)
        self.assertEqual(0, len(response.data['results']))
        self.assertEqual(0, response.data['count'])
