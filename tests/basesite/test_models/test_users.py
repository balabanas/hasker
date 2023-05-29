from django.contrib.auth.models import User
from django.core.files import File
from django.db import IntegrityError
from django.test import TestCase

from basesite.models import UserProfile
from hasker.settings.base import MEDIA_URL


class TestUser(TestCase):
    def test_email_unique(self):
        User.objects.create(email='test@df.com')
        with self.assertRaises(IntegrityError):
            User.objects.create(email='test@df.com')

    def test_no_orphane_user(self):
        with open('tests/basesite/test_models/test_logo.png', 'rb') as image_file:
            django_file = File(image_file)
            with self.assertRaises(IntegrityError):
                UserProfile.objects.create(avatar=django_file)  # no user profile w/o basic User

    def test_success_user_profile(self):
        with open('tests/basesite/test_models/test_logo.png', 'rb') as image_file:
            django_file = File(image_file)
            u = User.objects.create(email='test@df.com')
            up = UserProfile.objects.create(user=u, avatar=django_file)
            self.assertIn(f'{MEDIA_URL}avatars/tests/basesite/test_models/test_logo', up.avatar.url)