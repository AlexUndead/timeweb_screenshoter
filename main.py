from os.path import isfile
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from typing import Optional, Dict
from pydantic import HttpUrl, NonNegativeInt, PositiveInt

from tasks import get_screenshots_ids

app = FastAPI()


@app.get('/test')
def test_url():
    return {'msg': 'hello world'}


@app.post('/screenshot')
def create_screenshots(url: HttpUrl, level: Optional[NonNegativeInt] = 1):
    return {'taks_id': get_screenshots_ids.delay(url, level).task_id}


@app.get('/screenshot/{id}')
def get_screenshot(id: PositiveInt):
    path_file = f'./images/{id}.png'
    if isfile(path_file):
        return FileResponse(path_file)
    raise HTTPException(status_code=404, detail='Picture not found')


@app.get('/check/{id}')
def check_status(id: str):
    task = get_screenshots_ids.AsyncResult(id)
    if task.status == 'SUCCESS':
        return {'result': task.result}
    return {'status': task.status}
