from django.contrib.auth.models import User
from django.core.files import File
from django.db.utils import IntegrityError
from django.test import TestCase

from basesite.models import UserProfile, Tag
from hasker.settings.base import MEDIA_URL


class TestUsers(TestCase):
    def test_email_unique(self):
        User.objects.create(email='test@df.com')
        with self.assertRaises(IntegrityError):
            User.objects.create(email='test@df.com')

    def test_no_orphane_user(self):
        with open('tests/test_logo.png', 'rb') as image_file:
            django_file = File(image_file)
            with self.assertRaises(IntegrityError):
                UserProfile.objects.create(avatar=django_file)  # no user profile w/o basic User

    def test_success_user_profile(self):
        with open('tests/test_logo.png', 'rb') as image_file:
            django_file = File(image_file)
            u = User.objects.create(email='test@df.com')
            up = UserProfile.objects.create(user=u, avatar=django_file)
            self.assertIn(f'{MEDIA_URL}avatars/tests/test_logo', up.avatar.url)


class TestTag(TestCase):
    def test_tag_slug_unique(self):
        """
        Tests if 2 slightly different tags which might have the same slugs (due to omitted non-ASCII symbols),
         actually receive different ones
        :return:
        """
        t1 = Tag(tag='fooш')
        t2 = Tag(tag='foo')
        t1.save()
        t2.save()
        self.assertEqual(t1.slug, 'foo')
        self.assertEqual(t2.slug, 'foo1')
        with self.assertRaises(IntegrityError):
            t3 = Tag(tag='foo')  # tag should be unique
            t3.save()

#TODO: more tests next week
