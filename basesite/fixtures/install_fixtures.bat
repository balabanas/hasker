@REM python manage.py migrate basesite zero

@REM python manage.py dumpdata your_app.YourModel --indent 2 > your_fixture.json
@REM python manage.py dumpdata auth.user --indent 2 > basesite/fixtures/users.json



python manage.py loaddata basesite/fixtures/users.json
python manage.py loaddata basesite/fixtures/user_profile.json
python manage.py loaddata basesite/fixtures/tag.json
python manage.py loaddata basesite/fixtures/question.json
python manage.py loaddata basesite/fixtures/answer.json