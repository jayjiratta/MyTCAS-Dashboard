from playwright.sync_api import sync_playwright

def fetch_courses():
    url = "https://course.mytcas.com/"
    search_terms = ["วิศวกรรมปัญญาประดิษฐ์", "วิศวกรรมคอมพิวเตอร์"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=500)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(url)
        page.wait_for_selector("body")

        for term in search_terms:
            search_input = page.query_selector('input[type="search"], input[placeholder*="ค้นหา"], input')
            if search_input:
                search_input.fill(term)
                search_button = page.query_selector('.i-search')
                if search_button:
                    search_button.click()
                else:
                    search_input.press("Enter")
                page.wait_for_timeout(3000)

                page.wait_for_selector("ul.t-programs", timeout=10000)
                program_links = page.query_selector_all("ul.t-programs li a")

                if program_links:
                    program_hrefs = []
                    for i, link in enumerate(program_links, 1):
                        href = link.get_attribute("href")
                        program_hrefs.append(href)

                    print(f"=== List of all href for '{term}' ===")
                    for i, href in enumerate(program_hrefs, 1):
                        print(f"{i}. {href}")

                    with open(f"data/web-scraping/program_hrefs_{term}.txt", "w", encoding="utf-8") as f:
                        for href in program_hrefs:
                            f.write(f"{href}\n")
                else:
                    programs_ul = page.query_selector("ul.t-programs")
                    if programs_ul:
                        html_content = programs_ul.inner_html()
                        print("HTML content:")
                        print(html_content[:500] + "..." if len(html_content) > 500 else html_content)
                    else:
                        print("No ul.t-programs found")
            else:
                print("No search input found for term:", term)

        input()
        browser.close()

if __name__ == "__main__":
    fetch_courses()