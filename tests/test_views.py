import json
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import smart_str
from basesite.models import Question, Answer, Tag


def create_test_data():
    u = User.objects.create_user(username='testuser1', password="QWEr4$31", email='testuser1@test.com')
    t1 = Tag.objects.create(tag='tag1')
    t2 = Tag.objects.create(tag='Tag 2')
    q = Question.objects.create(author=u, title='Q title', message='Q content', votes=3)
    q.tags.set([t1, t2])
    q.save()
    Answer.objects.create(author=u, question=q, message='A to Q, content', correct=False)
    # q2 - created later but with more votes
    q2 = Question.objects.create(author=u, title='Q2 title', message='Q2 content', votes=2)
    Answer.objects.create(author=u, question=q2, message='A to Q2, content', correct=False)


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
        self.assertEqual(2, len(response.context_data['object_list']))
        self.assertEqual(2, len(response.context_data['trending_object_list']))

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


class QuestionTagListViewTest(TestCase):
    def test_response_no_result(self):
        response = self.client.get(reverse('tag-list', args=['tag-1']))
        self.assertEqual(200, response.status_code)
        expected_response_content = 'tag was not found'
        self.assertContains(response, expected_response_content)
        self.assertTemplateUsed(response, 'basesite/question_tag_list.html')


class QuestionCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_get_login_required_redirect(self):
        response = self.client.get(reverse('create'))
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('create')}")

    def test_get_logged(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('create'))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'basesite/question_form.html')

    def test_post_success(self):
        self.client.force_login(self.user)
        create_data = {
            'title': 'Question title',
            'message': 'Question message',
            'tags': ['a' * i for i in range(1, Question.max_tags + 1)]
        }
        response = self.client.post(reverse('create'), create_data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('question-detail', args=['1']))

    def test_post_validaton_errors(self):
        self.client.force_login(self.user)
        create_data = {
            'title': 'Question title',
            'message': 'Question message',
            'tags': ['a' * i for i in range(1, Question.max_tags + 2)]
        }
        response = self.client.post(reverse('create'), create_data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Maximum number of tags')


class QuestionDetailViewTest(TestCase):
    def test_not_exists(self):
        response = self.client.get(reverse('question-detail', args='1'))
        self.assertEqual(404, response.status_code)

    def test_get_success(self):
        create_test_data()
        response = self.client.get(reverse('question-detail', args='1'))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Q title')
        self.assertTemplateUsed(response, 'basesite/question_detail.html')


class SignUpViewTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse('sign-up'))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Sign Up')
        self.assertTemplateUsed(response, 'auth/user_form.html')

    def test_post_validation(self):
        signup_data = {
            'username': 'testuser',
            'email': 'testuser@t.com',
            'password1': 'PWQWwe#1',
            'password2': 'PQWwe#1',  # pwd mismatch
        }
        response: TemplateResponse = self.client.post(reverse('sign-up'), signup_data)
        self.assertEqual(200, response.status_code)
        self.assertIn("didn’t match", smart_str(response.content))
        signup_data['password2'] = signup_data['password1']
        response = self.client.post(reverse('sign-up'), signup_data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('list'))


class HaskerLoginViewTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Log In')
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_post_validation(self):
        create_test_data()
        login_data = {
            'username': 'testuser1',
            'password': 'QWEr4$31_',  # incorrect password
        }
        response: TemplateResponse = self.client.post(reverse('login'), login_data)
        self.assertEqual(200, response.status_code)
        self.assertIn("Please enter a correct username and password", smart_str(response.content))
        login_data['password'] = 'QWEr4$31'
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('list'))


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


class FuncViewAcceptAnswerTest(TestCase):
    def setUp(self) -> None:
        self.data = {
            'question_id': 1,
            'answer_id': 1,
        }
        self.user = User.objects.create_user(username='aa_testuser', password='testpas4Das')

    def test_post_login_required(self):
        response: TemplateResponse = self.client.post(reverse('accept-answer', args=[self.data['question_id'],
                                                                                     self.data['answer_id']]),
                                                      self.data)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Login required', content['result'])

    def test_post_not_found(self):
        self.client.force_login(self.user)
        response: TemplateResponse = self.client.post(reverse('accept-answer', args=[self.data['question_id'],
                                                                                     self.data['answer_id']]),
                                                      self.data)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Not found', content['result'])

    def test_post_question_user_mismatch(self):
        create_test_data()
        u = User.objects.get(username='aa_testuser')  # question created by `testuser1`
        self.client.force_login(u)
        response: TemplateResponse = self.client.post(reverse('accept-answer', args=[self.data['question_id'],
                                                                                     self.data['answer_id']]),
                                                      self.data)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Not found', content['result'])

    def test_post_success(self):
        create_test_data()
        u = User.objects.get(username='testuser1')
        self.client.force_login(u)
        response: TemplateResponse = self.client.post(reverse('accept-answer', args=[self.data['question_id'],
                                                                                     self.data['answer_id']]),
                                                      self.data)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Success', content['result'])


class FuncViewVoteTest(TestCase):
    def setUp(self) -> None:
        self.data_q = {
                    'instance_type': 'q',
                    'instance_id': 1,
                    'increment': 1,
        }
        self.data_a = {
                    'instance_type': 'a',
                    'instance_id': 1,
                    'increment': -1,
        }

        self.user = User.objects.create_user(username='v_testuser', password='testpas4Das')

    def test_post_login_required(self):
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_q['instance_id']]),
                                                      self.data_q)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Login required', content['result'])

    def test_post_wrong_data(self):
        self.client.force_login(self.user)
        self.data_q['increment'] = 2  # invalid increment
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_q['instance_id']]),
                                                      self.data_q)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Wrong request data', content['result'])

    def test_post_q_does_not_exist(self):
        self.client.force_login(self.user)
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_q['instance_id']]),
                                                      self.data_q)  # question does not exist
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Wrong request data', content['result'])

    def test_post_a_does_not_exist(self):
        self.client.force_login(self.user)
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_a['instance_id']]),
                                                      self.data_a)  # answe does not exist
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Wrong request data', content['result'])

    def test_post_q_upvote(self):
        self.client.force_login(self.user)
        create_test_data()
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_q['instance_id']]),
                                                      self.data_q)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Success', content['result'])
        # repeated attempt to upvote
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_q['instance_id']]),
                                                      self.data_q)
        content = json.loads(response.content)
        self.assertEqual('Already voted', content['result'])

    def test_post_a_downvote_upvote(self):
        self.client.force_login(self.user)
        create_test_data()
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_a['instance_id']]),
                                                      self.data_a)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual('Success', content['result'])  # downvoted
        # now, upvote
        self.data_a['increment'] = 1
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_a['instance_id']]),
                                                      self.data_a)
        content = json.loads(response.content)
        self.assertEqual('Success', content['result'])
        # upvote once again
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_a['instance_id']]),
                                                      self.data_a)
        content = json.loads(response.content)
        self.assertEqual('Success', content['result'])
        # and again ... now it is not possible
        response: TemplateResponse = self.client.post(reverse('vote', args=[self.data_a['instance_id']]),
                                                      self.data_a)
        content = json.loads(response.content)
        self.assertEqual('Already voted', content['result'])


class FuncViewTagTypeahead(TestCase):
    def test_get(self):
        create_test_data()
        response: TemplateResponse = self.client.get(f"{reverse('tag-typeahead')}?query=ta")
        content = json.loads(response.content)
        value_exists = any(d['value'] == 'tag1' for d in content)
        self.assertTrue(value_exists)
