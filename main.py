import io
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import HttpUrl, NonNegativeInt, PositiveInt
from botocore.exceptions import ClientError

from tasks import get_screenshots_ids
from screenshoter import get_file

app = FastAPI()


@app.get('/test')
def test_url():
    '''Тестовый метод для проверки роутинга'''
    return {'msg': 'hello world'}


@app.post('/screenshot')
def create_screenshots(url: HttpUrl, level: Optional[NonNegativeInt] = 1):
    '''Метод создания задачи для скриншотов'''
    return {'taks_id': get_screenshots_ids.delay(url, level).task_id}


@app.get('/screenshot/{screenshot_id}')
def get_screenshot(screenshot_id: PositiveInt):
    '''Метод получения скриншота'''
    try:
        file = get_file(f'{screenshot_id}.png')
        return StreamingResponse(io.BytesIO(file), media_type='image/png')
    except ClientError:
        raise HTTPException(status_code=404, detail='Picture not found')


@app.get('/check/{task_id}')
def check_task_status(task_id: str):
    '''Метод проверки статуса задачи'''
    task = get_screenshots_ids.AsyncResult(task_id)
    if task.status == 'SUCCESS':
        return {'result': task.result}
    return {'status': task.status}
