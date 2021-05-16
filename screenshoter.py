from io import BytesIO
from os import environ
from time import time
from urllib.parse import urlparse
from typing import Dict, List
from boto3 import Session
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')
S3_BUCKET = environ.get('S3_BUCKET')
PATH_TO_DRIVER = environ.get('PATH_TO_DRIVER')
PATH_TO_BINARY_DRIVER = environ.get('PATH_TO_BINARY_DRIVER')

s3_session = Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
s3_client = s3_session.client('s3')
s3_resource = s3_session.resource('s3')
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=950,700')
chrome_options.binary_location = PATH_TO_BINARY_DRIVER


def _get_site_address(url: str) -> str:
    '''Получение адреса сайта'''
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'


def _append_links(structured_links: Dict, links: List, level: int) -> None:
    '''Добавление ссылок в структуру ссылок сайта'''
    if not structured_links.get(level):
        structured_links[level] = links
    else:
        structured_links[level].append(links)


def get_file(name: str):
    '''Получение файла в байтах'''
    return s3_resource.Object(S3_BUCKET, name).get()['Body'].read()


def _check_url(url: str, site_address: str) -> bool:
    '''Проверка урла пренадлежности сайту'''
    if url:
        return url.startswith(site_address)
    return False


def _get_all_links(driver: Chrome) -> List:
    '''Получение всех ссылок со страницы'''
    return [
        link.get_attribute("href")
        for link in driver.find_elements_by_tag_name("a")
    ]


def _create_screenshot(driver: Chrome, url: str) -> str:
    '''Создание скриншота'''
    screenshot_name = str(int(time()))
    driver.get(url)
    with BytesIO(driver.get_screenshot_as_png()) as screenshot:
        s3_client.upload_fileobj(
            screenshot,
            S3_BUCKET,
            f'{screenshot_name}.png'
        )
        return screenshot_name


def create_screenshots(main_url: str, max_level: int) -> List:
    '''Создание скриншотов'''
    result = []
    site_address = _get_site_address(main_url)
    structured_links = {0: [site_address]}

    with Chrome(PATH_TO_DRIVER, options=chrome_options) as driver:
        for level in range(max_level):
            for url in set(structured_links[level]):
                try:
                    next_level = level + 1
                    screenshot_name = _create_screenshot(driver, url)
                    result.append(screenshot_name)
                    prepared_links = [
                        link for link in _get_all_links(driver)
                        if _check_url(link, site_address)
                    ]
                    if next_level <= max_level:
                        _append_links(
                            structured_links,
                            prepared_links,
                            next_level
                        )
                except WebDriverException:
                    continue
        return result
