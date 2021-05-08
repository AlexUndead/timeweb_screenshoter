import os
from celery import Celery
from screenshoter import create_screenshots

BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost')
RESULT_BACKEND = os.environ.get('RESULT_BACKEND', 'redis://localhost')

app = Celery('tasks', broker=BROKER_URL, backend=RESULT_BACKEND)
app.conf.update(task_track_started=True)


@app.task
def get_screenshots_ids(url: str, level: int):
    return create_screenshots(url, level)
