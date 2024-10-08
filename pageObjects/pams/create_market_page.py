from model.elements.button import Button
from model.elements.input import Input
from model.podio_item import PartnerFieldsPodio

from pageObjects.pams.add_new_market_page import AddMarketPage
from selenium.webdriver.chrome.webdriver import WebDriver


class CreateMarketPage(AddMarketPage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)

        self.username_input = Input(driver, '//input[@name="username"]')
        self.password_input = Input(driver, '//input[@name="password"]')
        self.password_repeat_input = Input(driver, '//input[@name="passwordRepeat"]')
        self.save_and_next_button = Button(driver, '//button[@data-name="button-save-and-next"]')
        self.finish_button = Button(driver, '//button[@data-name="button-finish"]')

    def add_password_and_username(self, username: str, password: str) -> None:
        self.username_input.wait_for_clickability(timeout=15)
        self.password_input.value = password
        self.password_repeat_input.value = password
        self.username_input.value = username

    def update_all_fields_in_create_view(self, market: str, podio_fields: PartnerFieldsPodio) -> None:
        self.order_email_input.wait_for_clickability(timeout=5)
        self.add_password_and_username(podio_fields.username, podio_fields.password)
        self.update_all_fields_in_add_view(market, podio_fields)
