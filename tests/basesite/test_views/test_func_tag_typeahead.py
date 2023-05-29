import json

from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse

from tests.basesite.utils import create_test_data


class FuncViewTagTypeahead(TestCase):
    def test_get(self):
        create_test_data()
        response: TemplateResponse = self.client.get(f"{reverse('tag-typeahead')}?query=ta")
        content = json.loads(response.content)
        value_exists = any(d['value'] == 'tag1' for d in content)
        self.assertTrue(value_exists)
