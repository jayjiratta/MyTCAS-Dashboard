
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "https://course.mytcas.com"

async def run():
    hrefs = Path("link/program_href.txt").read_text(encoding="utf-8").splitlines()
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for href in hrefs:
            url = BASE_URL + href
            print(f"Scraping: {url}")
            await page.goto(url)

            try:
                university = await page.locator('a[href^="/universities/"]').first.inner_text()
            except:
                university = ""
            try:
                faculty = await page.locator('a[href*="/faculties/"]').first.inner_text()
            except:
                faculty = ""
            try:
                field = await page.locator('a[href*="/fields/"]').first.inner_text()
            except:
                field = ""

            dt_dd = {}

            dt_elements = await page.locator("ul.body.t-program dt").all()
            dd_elements = await page.locator("ul.body.t-program dd").all()

            for dt, dd in zip(dt_elements, dd_elements):
                dt_text = (await dt.inner_text()).strip()
                dd_text = (await dd.inner_text()).strip()
                if dt_text and dd_text:
                    dt_dd[dt_text] = dd_text

            results.append({
                "url": url,
                "university": university,
                "faculty": faculty,
                "field": field,
                "details": dt_dd
            })

        await browser.close()

    output_path = Path("data/web-scraping/course_data.json")
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ DONE! Saved to {output_path.absolute()}")

asyncio.run(run())
