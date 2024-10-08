from typing import Self

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from model.elements.baseElement import BaseElement


class Checkbox(BaseElement):

    def __init__(self, driver: WebDriver, selector: str, locator: str = By.XPATH):
        super(Checkbox, self).__init__(driver, selector, locator)

    def format(self, *args) -> Self:
        formated_element = Checkbox(self.driver, self.selector.format(*args))
        formated_element.var_name = self.var_name
        return formated_element

    @property
    def is_checked(self) -> bool:
        return self.element.get_attribute('aria-checked') == 'true'

    def check(self) -> None:
        if not self.is_checked:
            self.element.click()

    def uncheck(self) -> None:
        if self.is_checked:
            self.element.click()
