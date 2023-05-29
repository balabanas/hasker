from django.urls import reverse, exceptions
from rest_framework import status
from rest_framework.test import APITestCase

from tests.basesite.utils import create_test_data, get_logged_user


class TestAnswerViewSet(APITestCase):
    def setUp(self) -> None:
        get_logged_user(self.client)

    def test_invalid_url(self):
        url = reverse('api-answer-list', args=(0,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        with self.assertRaises(exceptions.NoReverseMatch):
            reverse('api-answer-list', args=('not_a_number',))

    def test_unauthenticated(self):
        self.client.logout()
        url = reverse('api-answer-list', args=(0,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual({'detail'}, set(response.data.keys()))

    def test_question_not_exist(self):
        url = reverse('api-answer-list', args=(0, ))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual({'detail'}, set(response.data.keys()))

    def test_empty_response_ok(self):
        ids = create_test_data()
        url = reverse('api-answer-list', args=(ids['q3'], ))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data['results']))

    def test_fields_expected(self):
        ids = create_test_data()
        url = reverse('api-answer-list', args=(ids['q3'], ))
        response = self.client.get(url)
        fields_expected = ['count', 'next', 'previous', 'results', 'page_count']
        self.assertEqual(set(fields_expected), set(response.data.keys()))

    def test_return_answers(self):
        ids = create_test_data()
        url = reverse('api-answer-list', args=(ids['q2'], ))
        response = self.client.get(url)
        self.assertEqual(1, len(response.data['results']))

    def test_return_model_fields_expected(self):
        ids = create_test_data()
        url = reverse('api-answer-list', args=(ids['q2'], ))
        response = self.client.get(url)
        fields_expected = ['id', 'author', 'message', 'date_created', 'votes', 'correct']
        self.assertEqual(set(fields_expected), set(response.data['results'][0].keys()))
