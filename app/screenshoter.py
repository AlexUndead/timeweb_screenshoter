import io
from time import time
from typing import Dict, List
from urllib.parse import urlparse
from os import path, makedirs, environ
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

IMAGES_DIR = './images/'

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=900,800')
chrome_options.add_argument('--ignore-certificate-errors')


def _prepare_url(url: str) -> str:
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'


def _append_links(structure_links: Dict, links: List, level: int) -> None:
    if structure_links.get(level):
        structure_links[level].append(links)
    else:
        structure_links[level] = links


def _create_folder(func):
    def wrapper(*args, **kwargs):
        if not path.isdir(IMAGES_DIR):
            makedirs(IMAGES_DIR)
        return func(*args, **kwargs)

    return wrapper


@_create_folder
def create_screenshots(url: str, level: int) -> List:
    with webdriver.Remote('http://selenium:4444/wd/hub', options=chrome_options) as driver:
        result = []
        main_url = _prepare_url(url)
        structure_links = {0: [main_url]}

        for level in range(level):
            for url in set(structure_links[level]):
                driver.get(url)
                image_name = str(int(time()))
                driver.save_screenshot(IMAGES_DIR+f'{image_name}.png')
                result.append(image_name)
                all_links = [
                    link.get_attribute('href')
                    for link in driver.find_elements_by_tag_name('a')
                ]
                links = [link for link in all_links if link.startswith(main_url)]
                _append_links(structure_links, links, level + 1)
        return result
