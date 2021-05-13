import io
from os.path import isfile
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional, Dict
from pydantic import HttpUrl, NonNegativeInt, PositiveInt

from tasks import get_screenshots_ids
from screenshoter import IMAGES_DIR

app = FastAPI()


@app.get('/test')
def test_url():
    return {'msg': 'hello world'}


@app.post('/screenshot')
def create_screenshots(url: HttpUrl, level: Optional[NonNegativeInt] = 1):
    return {'taks_id': get_screenshots_ids.delay(url, level).task_id}


@app.get('/screenshot/{id}')
def get_screenshot(id: PositiveInt):
    return FileResponse(IMAGES_DIR+f'{id}.png')


@app.get('/check/{id}')
def check_status(id: str):
    task = get_screenshots_ids.AsyncResult(id)
    if task.status == 'SUCCESS':
        return {'result': task.result}
    return {'status': task.status}
