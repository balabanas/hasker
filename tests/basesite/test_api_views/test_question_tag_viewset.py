from django.urls import reverse, exceptions
from rest_framework import status
from rest_framework.test import APITestCase

from tests.basesite.utils import create_test_data, get_logged_user


class TestQuestionViewSet(APITestCase):
    def setUp(self) -> None:
        get_logged_user(self.client)

    def test_invalid_url(self):
        url = reverse('api-tag-list', args=(0,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        with self.assertRaises(exceptions.NoReverseMatch):
            reverse('api-tag-list', args=('not_a_number',))

    def test_unauthenticated(self):
        self.client.logout()
        url = reverse('api-tag-list', args=(0, ))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual({'detail'}, set(response.data.keys()))

    def test_question_not_exist(self):
        url = reverse('api-tag-list', args=(0, ))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual({'detail'}, set(response.data.keys()))

    def test_empty_response_ok(self):
        ids = create_test_data()
        url = reverse('api-tag-list', args=(ids['q2'], ))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_return_list_type(self):
        ids = create_test_data()
        url = reverse('api-tag-list', args=(ids['q2'], ))
        response = self.client.get(url)
        self.assertEqual('ReturnList', type(response.data).__name__)

    def test_return_tags(self):
        ids = create_test_data()
        url = reverse('api-tag-list', args=(ids['q1'], ))
        response = self.client.get(url)
        self.assertEqual(2, len(response.data))

    def test_return_expected_model_fields(self):
        ids = create_test_data()
        url = reverse('api-tag-list', args=(ids['q1'],))
        response = self.client.get(url)
        fields_expected = ['id', 'tag', 'slug']
        self.assertEqual(set(fields_expected), set(response.data[0].keys()))
