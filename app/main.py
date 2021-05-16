from os.path import isfile
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import HttpUrl, NonNegativeInt, PositiveInt

from tasks import get_screenshots_ids
from screenshoter import SCREENSHOTS_DIR

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
    screenshot_path = SCREENSHOTS_DIR+f'{screenshot_id}.png'
    if isfile(screenshot_path):
        return FileResponse(screenshot_path)
    raise HTTPException(status_code=404, detail='Screenshot not found')


@app.get('/check/{task_id}')
def check_task_status(task_id: str):
    '''Метод проверки статуса задачи'''
    task = get_screenshots_ids.AsyncResult(task_id)
    if task.status == 'SUCCESS':
        return {'result': task.result}
    return {'status': task.status}
