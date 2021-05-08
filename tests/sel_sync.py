import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

TEST_URLS = [
    "https://granelle-dev.idacloud.ru",
    "https://granelle-dev.idacloud.ru/objects/",
    "https://granelle-dev.idacloud.ru/objects/trinity2/",
    "https://granelle-dev.idacloud.ru/flats/",
    "https://granelle-dev.idacloud.ru/parking/",
    "https://granelle-dev.idacloud.ru/storages/",
    "https://granelle-dev.idacloud.ru/how-to-buy/mortgage/",
    "https://granelle-dev.idacloud.ru/press/news/",
    "https://granelle-dev.idacloud.ru/company/",
    "https://granelle-dev.idacloud.ru/agreement/",
]
PATH_TO_DRIVER = '/home/alex/selenium/chrome/90/chromedriver'
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--ignore-certificate-errors')


def run():
    i = 1 
    driver = webdriver.Chrome(PATH_TO_DRIVER, options=chrome_options)

    for url in TEST_URLS*10:
        driver.get(url)
        driver.save_screenshot(f'./images/{i}.png')
        i += 1

    driver.close()


if __name__ == "__main__":
    start = time.time()
    run()
    end = time.time()
    print(end - start)

