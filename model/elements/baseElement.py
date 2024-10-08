"""
BaseElement
"""
import inspect
import linecache

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASIC_TIMEOUT = 5


class BaseElement(object):
    """Base elements class contains all the common methods & attributes
    inherited by other elements
    """
    elements_collection = []
    element = None

    def __init__(self, driver: WebDriver, selector: str, locator: str):
        self.locator = locator
        self.selector = selector
        self.driver = driver
        frame = inspect.currentframe().f_back.f_back
        self.var_name = linecache.getline(frame.f_code.co_filename, frame.f_lineno).strip().split()[0]

    def __repr__(self) -> str:
        return f"<{self.var_name.replace('self.', '')}='{self.selector}>'"

    @property
    def element(self) -> WebElement:
        return self.wait_for_presence()

    def get_elements(self) -> list[WebElement]:
        self.elements_collection = self.driver.find_elements(self.locator, self.selector)
        return self.elements_collection

    def is_enabled(self) -> bool:
        return self.element.is_enabled()

    def click(self, timeout: int = 1) -> None:
        self.wait_for_clickability(timeout).click()

    def mouse_hover(self) -> None:
        webdriver.ActionChains(self.driver).move_to_element(self.element).perform()

    def get_attribute(self, name: str) -> str:
        return self.element.get_attribute(name)

    def is_clickable(self, timeout: int = BASIC_TIMEOUT) -> bool:
        try:
            return bool(self.wait_for_clickability(timeout))
        except TimeoutException:
            return False

    def wait_for_clickability(self, timeout: int = BASIC_TIMEOUT, error_msg: str = None) -> WebElement:
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((self.locator, self.selector)),
            f'{error_msg or ""}\n {self} is not visible after {timeout=}s.'
        )

    def wait_for_visibility(self, timeout: int = BASIC_TIMEOUT, error_msg: str = None) -> WebElement:
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((self.locator, self.selector)),
            f'{error_msg or ""}\n {self} is not visible after {timeout=}s.'
        )

    def is_visible(self, timeout: int = BASIC_TIMEOUT) -> bool:
        try:
            return bool(self.wait_for_visibility(timeout))
        except TimeoutException:
            return False

    def wait_for_invisibility(self, timeout: int = BASIC_TIMEOUT, error_msg: str = None) -> WebElement:
        return WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((self.locator, self.selector)),
            f'{error_msg or ""}\n{self} is not invisible after {timeout=}s.'
        )

    def is_not_visible(self, timeout: int = BASIC_TIMEOUT) -> bool:
        try:
            return bool(self.wait_for_invisibility(timeout))
        except TimeoutException:
            return False

    def wait_for_presence(self, timeout: int = BASIC_TIMEOUT, error_msg: str = None) -> WebElement:
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((self.locator, self.selector)),
            f'{error_msg or ""}\n{self} is not present after {timeout=}s.'
        )

    def is_present(self, timeout: int | float = BASIC_TIMEOUT) -> bool:
        try:
            return bool(self.wait_for_presence(timeout))
        except TimeoutException:
            return False

    def is_visible_now(self) -> bool:
        return self.element.is_displayed()

    @property
    def text(self) -> str:
        return self.element.text
