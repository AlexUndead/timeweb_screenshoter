import io
from boto3 import Session
from time import time
from typing import Dict, List
from selenium import webdriver
from urllib.parse import urlparse
from os import path, makedirs, environ
from selenium.webdriver.chrome.options import Options

AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')
S3_BUCKET = environ.get('S3_BUCKET', 'timeweb-screenshoter-images')
PATH_TO_DRIVER = environ.get('PATH_TO_DRIVER')
PATH_TO_BINARY_DRIVER = environ.get('PATH_TO_BINARY_DRIVER')

s3_session = Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
s3_client = s3_session.client('s3')
s3_resource = s3_session.resource('s3')
chrome_options = Options()

if not PATH_TO_DRIVER:
    PATH_TO_DRIVER = '/var/www/html/Projects/selenium-drivers/chrome/87/chromedriver'
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--ignore-certificate-errors')

if PATH_TO_BINARY_DRIVER:
    chrome_options.binary_location = PATH_TO_BINARY_DRIVER


def _prepare_url(url: str) -> str:
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'


def _append_links(structure_links: Dict, links: List, level: int) -> None:
    if structure_links.get(level):
        structure_links[level].append(links)
    else:
        structure_links[level] = links


def get_file(name: str):
    return s3_resource.Object(S3_BUCKET, name).get()['Body'].read()


def create_screenshots(url: str, level: int) -> List:
    with webdriver.Chrome(PATH_TO_DRIVER, options=chrome_options) as driver:
        result = []
        main_url = _prepare_url(url)
        structure_links = {0: [main_url]}

        for level in range(level):
            for url in set(structure_links[level]):
                driver.get(url)
                image_name = str(int(time()))
                with io.BytesIO(driver.get_screenshot_as_png()) as screenshot:
                    s3_client.upload_fileobj(screenshot, S3_BUCKET, f'{image_name}.png')
                result.append(image_name)
                all_links = [
                    link.get_attribute('href')
                    for link in driver.find_elements_by_tag_name('a')
                ]
                links = [link for link in all_links if link.startswith(main_url)]
                _append_links(structure_links, links, level + 1)
        return result
