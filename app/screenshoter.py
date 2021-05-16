from time import time
from typing import Dict, List, Callable
from urllib.parse import urlparse
from os import makedirs
from os.path import isdir
from selenium.webdriver import Remote
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException

SCREENSHOTS_DIR = "./images/"
FIREFOX_HUB_URL = "http://selenium:4444/wd/hub"

firefox_options = Options()
firefox_options.add_argument("--headless")
firefox_options.add_argument("--window-size=900,800")
firefox_options.add_argument("--ignore-certificate-errors")


def _get_site_address(url: str) -> str:
    '''Получение адреса сайта'''
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def _append_links(structure_links: Dict, links: List, level: int) -> None:
    '''Добавление ссылок в структуру ссылок сайта'''
    if not structure_links.get(level):
        structure_links[level] = links
    else:
        structure_links[level].append(links)


def _create_screenshot_folder(func: Callable) -> Callable:
    '''Создание папки для скриншотов'''
    def wrapper(*args, **kwargs):
        if not isdir(SCREENSHOTS_DIR):
            makedirs(SCREENSHOTS_DIR)
        return func(*args, **kwargs)

    return wrapper


def _check_url(url: str, site_address: str) -> bool:
    '''Проверка урла пренадлежности сайту'''
    if url:
        return url.startswith(site_address)
    return False


def _get_all_links(driver: Remote) -> List:
    return [
        link.get_attribute("href")
        for link in driver.find_elements_by_tag_name("a")
    ]


def _create_screenshot(driver: Remote, url: str) -> str:
    '''Создание скриншота'''
    screenshot_name = str(int(time()))
    driver.get(url)
    driver.save_screenshot(SCREENSHOTS_DIR + f"{screenshot_name}.png")

    return screenshot_name


@_create_screenshot_folder
def create_screenshots(main_url: str, max_level: int) -> List:
    '''Создание скриншотов'''
    result = []
    site_address = _get_site_address(main_url)
    structured_links = {0: [site_address]}

    with Remote(FIREFOX_HUB_URL, options=firefox_options) as driver:
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
