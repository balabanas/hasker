from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse

from tests.basesite.utils import create_test_data


class QuestionSearchListViewTest(TestCase):
    def test_get_not_found(self):
        response = self.client.get(f"{reverse('search')}?q=test")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'No questions found')
        self.assertTemplateUsed(response, 'basesite/search_results.html')

    def test_get_found(self):
        create_test_data()
        response = self.client.get(f"{reverse('search')}?{urlencode({'q': 'Q2 title'})}")
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'No questions found')
        self.assertEqual(1, len(response.context['page_obj']))
        self.assertTemplateUsed(response, 'basesite/search_results.html')

    def test_redirect_with_tag(self):
        create_test_data()
        response = self.client.get(f"{reverse('search')}?{urlencode({'q': 'tag:tag1'})}")
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('tag-list', args=['tag1']))
        response = self.client.get(response.url)
        self.assertEqual(200, response.status_code)
        tags_found_for_q1 = response.context['page_obj'][0].tags.all()
        tag1_found = any(t.tag == 'tag1' for t in tags_found_for_q1)
        self.assertTrue(tag1_found)
