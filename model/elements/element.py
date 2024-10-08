from typing import Self

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from model.elements.baseElement import BaseElement


class Element(BaseElement):

    def __init__(self, driver: WebDriver, selector: str, locator: str = By.XPATH):
        super(Element, self).__init__(driver, selector, locator)

    def format(self, *args) -> Self:
        formated_element = Element(self.driver, self.selector.format(*args))
        formated_element.var_name = self.var_name
        return formated_element
