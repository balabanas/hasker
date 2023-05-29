from django.contrib.auth.models import User

from basesite.models import Question, Answer, Tag


def create_test_data():
    """
    # Create some test data and return ids of created objects to avoid problems with referencing them in tests in
    case db ids are not reseted to 1 for every test, like in Postgres case
    :return:
    """
    u = User.objects.create_user(username='testuser1', password="QWEr4$31", email='testuser1@test.com')
    t1 = Tag.objects.create(tag='tag1')
    t2 = Tag.objects.create(tag='Tag 2')
    q1 = Question.objects.create(author=u, title='Q title', message='Q content', votes=3)
    q1.tags.set([t1, t2])
    q1.save()
    a1 = Answer.objects.create(author=u, question=q1, message='A to Q, content', correct=False)

    # q2 - created later but with more votes
    q2 = Question.objects.create(author=u, title='Q2 title', message='Q2 content', votes=2)
    a2 = Answer.objects.create(author=u, question=q2, message='A to Q2, content', correct=False)

    # q3 - has no answers yet
    q3 = Question.objects.create(author=u, title='Q3 title', message='Q3 content', votes=1)
    return {
        'u': u.id,
        't1': t1.id,
        't2': t2.id,
        'q1': q1.id,
        'q2': q2.id,
        'a1': a1.id,
        'a2': a2.id,
        'q3': q3.id,
    }


def get_logged_user(client):
    u = User.objects.create_user(username='user_to_login', password="QWEr4$31", email='user_to_login@test.com')
    client.force_login(u)
