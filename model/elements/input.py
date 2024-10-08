from typing import Self

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from model.elements.baseElement import BaseElement


class Input(BaseElement):

    def __init__(self, driver: WebDriver, selector: str, locator: str = By.XPATH):
        super(Input, self).__init__(driver, selector, locator)

    def format(self, *args) -> Self:
        formated_element = Input(self.driver, self.selector.format(*args))
        formated_element.var_name = self.var_name
        return formated_element

    @property
    def value(self) -> str:
        return self.get_attribute('value')

    @value.setter
    def value(self, text: str) -> None:
        del self.value
        self.driver.find_element(self.locator, self.selector).send_keys(text)

    @value.deleter
    def value(self) -> None:
        self.driver.find_element(self.locator, self.selector).clear()
