from django.test import TestCase
from django.urls import reverse

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
