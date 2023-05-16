# Hasker: Poor Man's Stackoverflow
Q&A site as Django application.

![img.png](docs/img/img.png)


## Build/Run instructions
### demo.env file
The repo comes with `demo.env` file. Use settings defined there or set your own before run.

###Run
The soluton is shipped in 3 Docker containers:
 * web (with django application)
 * db (postgres)
 * nginx (with nginx)

To spin them up, from the source root (where the docker-compose.yml file is located), run:
 * `docker compose up`

Then in your browser, open:
 * `http://localhost:8000/` 

### Fixtures
The repo comes with pre-populated database content for demo purposes. Thanks to `chatGPT` for providing necessary mockups for questions and answers! This content in form of fixtures is automatically (re)installed to the database on every run of the `web` docker container.

You may try to work under several pre-created demo users:
* `testuser1` / `PWDtU234%%`
* `testuser2` / `2PWDtU234%%`
* `testuser3` / `3PWDtU234%%`

## Run tests locally
Create hasker/settings/local.py with the contents:
```python
from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
Run:
* `python manage.py test --settings hasker.settings.local`


## Dependencies and acknowledgments
1. Python (v3.10)
2. Django (v4.1.7) A high-level Python web framework - [Official Website](https://www.djangoproject.com/)
3. Bootstrap (v5.0.2) - Front-end CSS framework - [Official Website](https://getbootstrap.com/)
4. PostgreSQL (v15.3)
5. psycopg2 (v2.9.6)
6. Docker (v20.10.22)
7. Docker Compose (v2.15.1)
8. uWSGI (v2.0.21)
9. ChatGPT (ChatGPT May 12 Version) [Official Website](https://chat.openai.com/)


All dependencies are distributed under their respective licenses.
