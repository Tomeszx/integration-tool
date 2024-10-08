from typing import Self

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from model.elements.baseElement import BaseElement


class Button(BaseElement):

    def __init__(self, driver: WebDriver, selector: str, locator: str = By.XPATH):
        super(Button, self).__init__(driver, selector, locator)

    def format(self, *args) -> Self:
        formated_element = Button(self.driver, self.selector.format(*args))
        formated_element.var_name = self.var_name
        return formated_element
