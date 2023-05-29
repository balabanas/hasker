from django.test import TestCase
from django.urls import reverse


class QuestionTagListViewTest(TestCase):
    def test_response_no_result(self):
        response = self.client.get(reverse('tag-list', args=['tag-1']))
        self.assertEqual(200, response.status_code)
        expected_response_content = 'tag was not found'
        self.assertContains(response, expected_response_content)
        self.assertTemplateUsed(response, 'basesite/question_tag_list.html')