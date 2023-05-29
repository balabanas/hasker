from django.db.utils import IntegrityError
from django.test import TestCase

from basesite.models import Tag


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
