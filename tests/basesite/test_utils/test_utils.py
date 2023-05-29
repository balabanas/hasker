from unittest import TestCase
from hasker.utils import read_env_file


class TestUtils(TestCase):
    def test_parse_file_read_env_file(self):
        env_vars = read_env_file('tests/basesite/test_utils/test.env')
        self.assertEqual('sk', env_vars['DJANGO_SECRET_KEY'])
        self.assertEqual('localhost', env_vars['DJANGO_ALLOWED_HOSTS'].split(',')[0])
        with self.assertRaises(KeyError):
            _ = env_vars['DJANGO_DEBUG']  # commented setting
        self.assertEqual('postgres', env_vars['POSTGRES_USER'])  # correctly read after empty string
