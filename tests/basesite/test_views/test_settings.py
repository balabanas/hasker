from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class SettingsViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='settings_testuser', password='testpas4Das')

    def test_get_login_required_redirect(self):
        response = self.client.get(reverse('settings'))
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('settings')}")

    def test_get_success(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('settings'))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Settings')
        self.assertContains(response, self.user.username)
        self.assertTemplateUsed(response, 'auth/user_edit_form.html')
