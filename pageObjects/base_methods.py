from __future__ import annotations
import logging

from io import BytesIO
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from utilites.config_parser import get_config

logging.getLogger("httpx").setLevel(logging.ERROR)


class BaseMethods:

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def open(self, desired_path: str) -> str:
        base_url = get_config('pams_urls_and_paths', 'main_page')
        self.driver.get(f'{base_url}{desired_path}')

        return base_url

    def make_screen(self, title: str) -> BytesIO:
        self.driver.execute_script("document.body.style.zoom = '0.50'")
        origin_size = self.driver.get_window_size()
        full_height = int(self.driver.execute_script("return document.body.scrollHeight"))

        self.driver.set_window_size(1920, full_height)
        screen = BytesIO(self.driver.get_screenshot_as_png())
        screen.name = title

        self.driver.set_window_size(origin_size['width'], origin_size['height'])
        self.driver.execute_script("document.body.style.zoom = '1'")

        return screen

    def wait_for_ready_state(self, timeout=5, state='complete') -> None:
        wait = WebDriverWait(self.driver, timeout)
        func = lambda driver: driver.execute_script('return document.readyState') == state
        wait.until(func, f"Document did not load to readyState for {timeout}s")
