from model.elements.button import Button
from model.elements.input import Input
from pageObjects.base_methods import BaseMethods
from selenium.webdriver.chrome.webdriver import WebDriver
from utilites.config_parser import get_config


class LoginPage(BaseMethods):

    def __init__(self, driver: WebDriver, credentials: dict):
        super().__init__(driver)
        self.credentials = credentials

        self.username_input = Input(driver, '//*[@name="username"]')
        self.password_input = Input(driver, '//*[@name="password"]')
        self.login_button = Button(driver, '//button[@data-name="button-login-form"]')

    def login(self) -> None:
        self.open('')
        self.password_input.wait_for_clickability(timeout=5)
        self.username_input.value = get_config('credentials', 'username_pams')
        self.password_input.value = get_config('credentials', 'password_pams')
        self.login_button.click()
        self.password_input.wait_for_invisibility(timeout=3)
