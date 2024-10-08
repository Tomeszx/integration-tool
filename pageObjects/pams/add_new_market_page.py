import os
import pandas as pd

from model.elements.button import Button
from model.elements.dropdown import Dropdown

from result import Ok, Result, is_err, Err
from selenium.webdriver.chrome.webdriver import WebDriver

from model.podio_item import PartnerFieldsPodio
from pageObjects.pams.edit_market_page import EditMarketPage

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('/pageObjects', '')


class AddMarketPage(EditMarketPage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)

        self.vat_zone_dropdown = Dropdown(driver, '//div[@data-name="vatZone"]/button')
        self.vat_zone_disabled = Button(driver, '//div[@data-name="vatZone"]/button[@disabled]')
        self.add_market_button = Button(driver, '//button[@data-name="button-create-market"]')

    def go_to_form_view(self) -> None:
        self.add_market_button.click(timeout=2)

    def update_vat_zone(self, current_market: str, home_market: str) -> None:
        with open(f"{BASE_PATH}/config/vat_zones.csv", "r") as file:
            vat_zones = pd.read_csv(file, index_col=0)
            vat_zone_dict = vat_zones.get(home_market, {})
            vat_zone_value = vat_zone_dict.get(current_market, 'EU')
            self.vat_zone_dropdown.open().select_option(vat_zone_value)

    def update_all_fields_in_add_view(self, current_market: str, podio_fields: PartnerFieldsPodio) -> None:
        self.vat_zone_dropdown.wait_for_visibility(timeout=15)
        if self.vat_zone_dropdown.is_enabled():
            self.update_vat_zone(current_market, podio_fields.home_market)
        self.update_all_fields_in_edit_view(current_market, podio_fields)
