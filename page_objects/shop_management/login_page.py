from page_objects.base_methods import BaseMethods, Locator
from selenium.webdriver.chrome.webdriver import WebDriver
from utilites.config_parser import get_config


class LoginPage(BaseMethods):
    username_input = Locator('username_input', arg='//*[@name="username"]')
    password_input = Locator('password_input', arg='//*[@name="password"]')
    login_button = Locator('login_button', arg='//button[@data-id="button-login-form"]')

    def __init__(self, driver: WebDriver, credentials: dict):
        super().__init__(driver)
        self.credentials = credentials

    def login(self) -> None:
        self.open('')
        self.wait_for_clickability(LoginPage.password_input)
        self.write(self.username_input, get_config('credentials', 'username_shop_management'))
        self.write(self.password_input, get_config('credentials', 'password_shop_management'))
        self.wait_for_clickability(self.login_button).click()
        self.wait_for_invisibility(self.password_input)
