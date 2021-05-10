import io
from os.path import isfile
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional, Dict
from pydantic import HttpUrl, NonNegativeInt, PositiveInt

from tasks import get_screenshots_ids
from screenshoter import get_file

app = FastAPI()


@app.get('/test')
def test_url():
    return {'msg': 'hello world'}


@app.post('/screenshot')
def create_screenshots(url: HttpUrl, level: Optional[NonNegativeInt] = 1):
    return {'taks_id': get_screenshots_ids.delay(url, level).task_id}


@app.get('/screenshot/{id}')
def get_screenshot(id: PositiveInt):
    try:
        file = get_file(f'{id}.png')
        return StreamingResponse(io.BytesIO(file), media_type='image/png')
    except:
        raise HTTPException(status_code=404, detail='Picture not found')


@app.get('/check/{id}')
def check_status(id: str):
    task = get_screenshots_ids.AsyncResult(id)
    if task.status == 'SUCCESS':
        return {'result': task.result}
    return {'status': task.status}
