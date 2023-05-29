from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse

from tests.basesite.utils import create_test_data


class QuestionListViewTest(TestCase):
    def test_response_no_questions(self):
        response = self.client.get(reverse('list'))
        self.assertEqual(200, response.status_code)
        expected_response_content = 'No questions found'
        self.assertContains(response, expected_response_content)
        self.assertTemplateUsed(response, 'basesite/question_list.html')

    def test_response_question_created(self):
        create_test_data()
        response: TemplateResponse = self.client.get(reverse('list'))
        self.assertEqual(200, response.status_code)
        expected_response_content = 'Q title'
        self.assertContains(response, expected_response_content)
        self.assertEqual('-date_created', response.context_data['ordering'])
        self.assertEqual(3, len(response.context_data['object_list']))
        self.assertEqual(3, len(response.context_data['trending_object_list']))

    def test_response_ordering(self):
        create_test_data()
        response: TemplateResponse = self.client.get(reverse('list'))
        self.assertEqual(200, response.status_code)
        # we'll find Q before Q2 in the page source as we've created it earlier
        idx1 = response.content.find(b'Q title')
        idx2 = response.content.find(b'Q2 title')
        self.assertGreater(idx1, idx2)
        # yet, in trending Q2 will be earlier that Q due to higher votes
        trending_idx = response.content.index(b'Trending')
        idx1 = response.content.find(b'Q title', trending_idx)
        idx2 = response.content.find(b'Q2 title', trending_idx)
        self.assertGreater(idx2, idx1)
        # now, change ordering
        response: TemplateResponse = self.client.get(reverse('list') + '?ordering=-votes')
        self.assertEqual(200, response.status_code)
        idx1 = response.content.find(b'Q title')
        idx2 = response.content.find(b'Q2 title')
        self.assertGreater(idx2, idx1)
        self.assertEqual('-votes', response.context_data['ordering'])
        # but the trending is still the same
        trending_idx = response.content.index(b'Trending')
        idx1 = response.content.find(b'Q title', trending_idx)
        idx2 = response.content.find(b'Q2 title', trending_idx)
        self.assertGreater(idx2, idx1)
