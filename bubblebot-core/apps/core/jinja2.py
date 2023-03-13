from datetime import datetime
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.conf import settings
from jinja2 import Environment


def date(datetime: datetime, date_format: str = '%Y-%m-%d %H:%M:%S'):
    return datetime.strftime(date_format)


def run_time(start_time: datetime):
    return str(datetime.now() - start_time).split(".")[0]


def status(status_code):
    if status_code == 1:
        result = ""


def media(path):
    return f"{settings.MEDIA_URL}{path}"


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            'static': staticfiles_storage.url,
            'url': reverse,
            'media': media,
        }
    )
    env.filters['date'] = date
    env.filters['run_time'] = run_time
    return env
