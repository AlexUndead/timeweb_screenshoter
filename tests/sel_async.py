import time

import asyncio
from pyppeteer import launch

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


async def run():
    i = 1 

    browser = await launch({
        'ignoreHTTPSErrors': True,
        'args': ['--window-size=1980,1080']
    })
    page = await browser.newPage()
    await page.setViewport({'width': 1980, 'height': 1080})

    for url in TEST_URLS*10:
        await page.goto(url)
        #await page.setViewport({'width': 1980, 'height': 1080})
        await page.screenshot({'path': f'./images/{i}.png'})
        i += 1

    await browser.close()

if __name__ == "__main__":
    start = time.time()
    asyncio.get_event_loop().run_until_complete(run())
    end = time.time()
    print(end - start)
