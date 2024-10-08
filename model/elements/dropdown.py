from typing import Self

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from model.elements.baseElement import BaseElement


class Dropdown(BaseElement):

    def __init__(self, driver: WebDriver, selector: str, locator: str = By.XPATH):
        super(Dropdown, self).__init__(driver, selector, locator)

    def format(self, *args) -> Self:
        formated_element = Dropdown(self.driver, self.selector.format(*args))
        formated_element.var_name = self.var_name
        return formated_element

    def open(self) -> Self:
        self.click()
        return self

    def select_option(self, option: str) -> None:
        option_xpath = (By.XPATH, f'{self.selector}/../div//div//span[text()="{option}"]')
        WebDriverWait(self.driver, 2).until(
            EC.element_to_be_clickable(option_xpath), f'{option=} is not present'
        ).click()

    @property
    def selected_option(self) -> str:
        selected_option = self.element.find_element(By.XPATH, f'./span')
        return selected_option.get_attribute('innerText')