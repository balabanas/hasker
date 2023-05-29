import base64

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tests.basesite.utils import create_test_data, get_logged_user


class TestAPIRootView(APITestCase):
    def setUp(self) -> None:
        get_logged_user(self.client)

    def test_unauthenticated(self):
        self.client.logout()
        url = reverse('api-root')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual({'detail'}, set(response.data.keys()))

    def test_basic_authentication(self):
        self.client.logout()
        create_test_data()
        url = reverse('api-root')
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

    def test_invalid_url(self):
        url = reverse('api-root', args=(0,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_response_ok(self):
        url = reverse('api-root')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
