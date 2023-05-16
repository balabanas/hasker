@REM python manage.py migrate basesite zero

@REM python manage.py dumpdata --settings hasker.settings.local your_app.YourModel --indent 2 > your_fixture.json
@REM python manage.py dumpdata auth.user --indent 2 > basesite/fixtures/users.json



@REM python manage.py loaddata basesite/fixtures/users.json
@REM python manage.py loaddata basesite/fixtures/user_profile.json
@REM python manage.py loaddata basesite/fixtures/tag.json
@REM python manage.py loaddata basesite/fixtures/question.json
@REM python manage.py loaddata basesite/fixtures/answer.json

python manage.py loaddata basesite/fixtures/user.json
python manage.py loaddata basesite/fixtures/userprofile.json
python manage.py loaddata basesite/fixtures/tag.json
python manage.py loaddata basesite/fixtures/question.json
python manage.py loaddata basesite/fixtures/answer.json