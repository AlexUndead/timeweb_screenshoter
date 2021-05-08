from os import path, makedirs
from time import time
from typing import Dict, List
from selenium import webdriver
from urllib.parse import urlparse
from selenium.webdriver.chrome.options import Options

PATH_TO_DRIVER = '/home/alex/selenium/chrome/90/chromedriver'
PATH_TO_IMAGE = './images/'
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--ignore-certificate-errors')


def _prepare_url(url: str) -> str:
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'


def _append_links(structure_links: Dict, links: List, level: int) -> None:
    if structure_links.get(level):
        structure_links[level].append(links)
    else:
        structure_links[level] = links


def _check_folder_image(func):
    def create_folder(*args, **kwargs):
        if not path.exists(PATH_TO_IMAGE):
            makedirs(PATH_TO_IMAGE)
        return func(*args, **kwargs)
    return create_folder


@_check_folder_image
def create_screenshots(url: str, level: int) -> List:
    with webdriver.Chrome(PATH_TO_DRIVER, options=chrome_options) as driver:
        result = []
        main_url = _prepare_url(url)
        structure_links = {0: [main_url]}

        for level in range(level):
            for url in set(structure_links[level]):
                driver.get(url)
                image_name = str(int(time()))
                driver.save_screenshot(f'{PATH_TO_IMAGE}{image_name}.png')
                result.append(image_name)
                all_links = [
                    link.get_attribute('href')
                    for link in driver.find_elements_by_tag_name('a')
                ]
                links = [link for link in all_links if link.startswith(main_url)]
                _append_links(structure_links, links, level + 1)
        return result
