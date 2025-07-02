from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time

def fetch_html_with_selenium(url, driver_path="msedgedriver.exe", wait_time=6):
    options = Options()
    options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")

    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(wait_time)
        html = driver.page_source
    finally:
        driver.quit()

    return html

