import os
import pandas as pd

from page_objects.base_methods import Locator
from result import Ok, Result, is_err, Err
from selenium.webdriver.chrome.webdriver import WebDriver

from page_objects.shop_management.edit_location_page import EditLocationPage

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('/page_objects', '')


class AddLocationPage(EditLocationPage):
    vat_zone_dropdown = Locator('vat_zone_dropdown', arg='//div[@data-id="vatZone"]')
    vat_zone_disabled = Locator('vat_zone_disabled', arg='//div[@data-id="vatZone"]/button[@disabled]')
    add_location_button = Locator('add_location_button', arg='//button[@data-id="button-create-location"]')

    def __init__(self, driver: WebDriver, podio_data: dict):
        super().__init__(driver, podio_data)

    def open_specific_market(self):
        converted_market = self.location.replace('UK', 'GB').replace('SHWRM', 'PL')
        locator = self.location_selector.__format__(converted_market.upper())
        self.wait_for_clickability(locator).click()

        if add_market := self.get_elements(self.add_location_button):
            add_market[0].click()
        elif edit_market := self.get_elements(self.edit_market_button):
            edit_market[0].click()

    def update_vat_zone(self) -> Result[None | str, str]:
        try:
            self.wait_for_clickability(self.vat_zone_dropdown, 15)
            if self.get_elements(self.vat_zone_disabled):
                return Ok('The vat zone dropdown is disabled. There is no need to update this field.')

            with open(f"{BASE_PATH}/additional_files/vat_zones.csv", "r") as file:
                vat_zones = pd.read_csv(file, index_col=0)
                vat_zone_dict = vat_zones.get(self.podio_data['Home_Market'], {})
                vat_zone_value = vat_zone_dict.get(self.location, 'EU')
                self.select(self.vat_zone_dropdown, vat_zone_value)
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_all_fields_in_add_view(self) -> Result[None, str]:
        try:
            self.wait_for_clickability(self.vat_zone_dropdown, 15)
            results = [
                self.update_vat_zone(),
                self.update_all_fields_in_edit_view()
            ]
        except Exception as e:
            return self.handle_exception(e)

        errors = "\n".join(result.err_value for result in results if is_err(result))
        if errors:
            return Err(errors)
        return Ok(None)
