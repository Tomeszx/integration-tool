from __future__ import annotations
import logging
import traceback
from concurrent.futures import as_completed, ThreadPoolExecutor

from api_objects.google_sheet_api import upload_file
from io import BytesIO
from result import Err, Ok, Result, is_err
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from utilites.config_parser import get_config

logging.getLogger("httpx").setLevel(logging.ERROR)


class Locator:
    def __init__(self, name: str, locator_type: str = By.XPATH, arg: str = None):
        self.value = locator_type, arg
        self.name = name

    def __format__(self, format_spec):
        return Locator(self.name, self.value[0], self.value[1].format(format_spec))

    def __iter__(self) -> tuple[By, str]:
        yield from self.value

    def __getitem__(self, item):
        return self.value[item]


class BaseMethods:

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def open(self, desired_path: str) -> str:
        base_url = get_config('shop_management_urls_and_paths', 'main_page')
        self.driver.get(f'{base_url}{desired_path}')

        return base_url

    def get_element(self, locator: Locator) -> WebElement:
        return self.driver.find_element(*locator)

    def get_elements(self, locator: Locator) -> [WebElement]:
        return self.driver.find_elements(*locator)

    def get_attribute(self, locator: Locator, attribute_name: str) -> str:
        return self.get_element(locator).get_attribute(attribute_name)

    def click(self, locator: Locator) -> Locator:
        self.get_element(locator).click()
        return locator

    def check(self, locator: Locator, is_checked: bool) -> Locator:
        if self.get_attribute(locator, 'aria-checked') != f'{is_checked}'.lower():
            self.click(locator)
        return locator

    def select(self, locator: Locator, option: str) -> None:
        self.click(locator)
        name = f'{locator.name} - {option=}'
        self.wait_for_clickability(Locator(name, arg=f'.//span/span[text()="{option}"]'), 5).click()

    def write(self, locator: Locator, value: str) -> None:
        element = self.driver.find_element(*locator)
        element.clear()
        element.send_keys(value)

    def clear_input(self, locator: Locator) -> None:
        self.driver.find_element(*locator).clear()

    def wait_for_visibility(self, locator: Locator, timeout=15) -> WebElement:
        message = f'{locator.name} is not visible after {timeout=}s'
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator.value), message)

    def wait_for_clickability(self, locator: Locator, timeout=15) -> WebElement:
        message = f'Can not click on {locator.name} after {timeout=}s'
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator.value), message)

    def wait_for_invisibility(self, locator: Locator, timeout=15) -> None:
        message = f'{locator.name} should disappear, but is still displayed after {timeout=}s'
        WebDriverWait(self.driver, timeout).until_not(EC.visibility_of_element_located(locator.value), message)

    def make_screen(self, title: str) -> BytesIO:
        origin_size = self.driver.get_window_size()
        full_height = int(self.driver.execute_script("return document.body.scrollHeight"))

        if full_height > origin_size['height']:
            self.driver.set_window_size(1920, full_height)
        screen = BytesIO(self.driver.get_screenshot_as_png())
        screen.name = title

        self.driver.set_window_size(origin_size['width'], origin_size['height'])

        return screen

    def handle_exception(self, exception: Exception) -> Err:
        print(traceback.format_exc())
        error_str = f"{exception.__class__.__name__} -> {str(exception).split('Stacktrace')[0]}"
        screen_url = upload_file(self.make_screen(f'{error_str}'))
        return Err(f'Issue while updating vat zone. Screenshot: {screen_url}\nMessage: {error_str}')

    @staticmethod
    def _get_comment_from_output(error_comments: dict, success_comments: dict) -> Result[str, str]:
        comment = ""
        for comment_to_add, markets in success_comments.items():
            comment += f"# The msg from markets [{', '.join(markets)}]:\n{comment_to_add}\n\n"
            if not comment_to_add:
                comment += "Nothing was changed.\n\n"
        if error_comments:
            for error_comment, markets in error_comments.items():
                comment += f"\n\n# The msg from markets [{', '.join(markets)}]\n{error_comment}"
            return Err(comment)
        return Ok(comment)

    def process_output(self, results: list) -> Result[str, str]:
        error_comments, success_comments = {}, {}
        for result in results:
            try:
                if is_err(result[1]) and result[1].value not in error_comments:
                    error_comments[result[1].value] = [result[0]]
                elif is_err(result[1]):
                    error_comments[result[1].value].append(result[0])
                elif result[1].value not in success_comments:
                    success_comments[result[1].value] = [result[0]]
                else:
                    success_comments[result[1].value].append(result[0])
            except AttributeError as e:
                raise AttributeError(f'{type(result)=} {result=}') from e
        return self._get_comment_from_output(error_comments, success_comments)
