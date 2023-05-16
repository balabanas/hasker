#!/bin/bash

python manage.py loaddata basesite/fixtures/user.json
python manage.py loaddata basesite/fixtures/userprofile.json
python manage.py loaddata basesite/fixtures/tag.json
python manage.py loaddata basesite/fixtures/question.json
python manage.py loaddata basesite/fixtures/answer.json