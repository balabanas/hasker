python manage.py dumpdata --settings hasker.settings.local --indent 2 > basesite/fixtures/user.json auth.user
python manage.py dumpdata --settings hasker.settings.local --indent 2 > basesite/fixtures/userprofile.json basesite.userprofile
python manage.py dumpdata --settings hasker.settings.local --indent 2 > basesite/fixtures/tag.json basesite.tag
python manage.py dumpdata --settings hasker.settings.local --indent 2 > basesite/fixtures/question.json basesite.question
python manage.py dumpdata --settings hasker.settings.local --indent 2 > basesite/fixtures/answer.json basesite.answer


