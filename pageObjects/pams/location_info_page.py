import contextlib

from result import Err, Result, Ok
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from model.elements.button import Button
from model.elements.dropdown import Dropdown
from model.elements.element import Element
from model.elements.input import Input
from pageObjects.base_methods import BaseMethods

MARKETS_NAMES = {
    "NL": "Netherlands", "DK": "Denmark", "SE": "Sweden", "BE": "Belgium", "FR": "France", "IT": "Italy",
    "ES": "Spain", "DE": "Germany", "PL": "Poland", "UK": "United Kingdom", "CH": "Switzerland",
    "FI": "Finland", "CN": "China", "NO": "Norway", "US": "United States"
}


class LocationInfoPage(BaseMethods):

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

        self.core_market_text = Element(driver, '//*[@data-name="preview-primary-core-platform"]')
        self.core_market_id_text = Element(driver, '//p[@data-name="preview-primary-location-id"]')
        self.shop_id_cell = Element(driver, '//div[contains(@data-name, "shop-id-")]/p[text()="{}"]/..')
        self.market_id_text = Element(driver, '//div[@data-name="shop-id-{}"]')
        self.market_ids_text = Element(driver, '//div[contains(@data-name, "shop-id-")]')
        self.location_name_input = Input(driver, '//input[@name="name"]')
        self.core_market_dropdown = Dropdown(driver, '//div[@data-name="partner-core-market"]')
        self.local_currency_dropdown = Dropdown(driver, '//div[@data-name="localCurrency"]')
        self.source_language_dropdown = Dropdown(driver, '//div[@data-name="sourceLanguage"]')
        self.save_and_next_button = Button(driver, '//button[@data-name="button-save-and-next"]')
        self.loading_image = Element(driver, '//label[text()="Sales Channel additional information"]/..//div/svg')

    def add_location_info(self, core_market: str, partner_name: str) -> None:
        self.location_name_input.wait_for_clickability(timeout=15)

        self.location_name_input.value = partner_name
        self.core_market_dropdown.open().select_option(MARKETS_NAMES[core_market])
        self.local_currency_dropdown.open().select_option('EUR')
        self.source_language_dropdown.open().select_option('English')

    def save_location(self) -> None:
        self.save_and_next_button.click()
        self.location_name_input.wait_for_invisibility(timeout=2)

    def get_location_id(self) -> str:
        return self.driver.current_url.split("/")[5]

    def get_core_market(self) -> str:
        core_market_full_name = self.core_market_text.get_attribute('innerText')
        core_market_index = list(MARKETS_NAMES.values()).index(core_market_full_name)
        core_market_short_name = list(MARKETS_NAMES)[core_market_index]

        return core_market_short_name

    def check_if_any_market_is_loading(self) -> Result[str, str]:
        for market in MARKETS_NAMES:
            market_elem = self.market_id_text.format(market.replace('UK', 'GB'))
            if not market_elem.is_present(timeout=0.1):
                return Err(f'The {market=} is still loading')
        return Ok('')

    def get_displayed_ids(self) -> dict:
        self.core_market_text.wait_for_presence(timeout=5)

        shop_ids = {}
        for shop_id_elem in self.market_ids_text.get_elements():
            if shop_id_elem.text.isdigit():
                market = shop_id_elem.get_attribute('data-name').split('shop-id-')[1]
                shop_ids[market.replace('GB', 'UK')] = shop_id_elem.text
        return shop_ids

    def wait_for_ids(self, pams_id: str) -> dict:
        self.open(f'/preview/{pams_id}/info')
        self.core_market_text.wait_for_visibility(timeout=5)

        core_market_short_name = self.get_core_market()
        with contextlib.suppress(TimeoutException):
            self.market_id_text.format(core_market_short_name).wait_for_presence(timeout=30)

        created_ids = self.get_displayed_ids()
        primary_location_id = self.core_market_id_text.text.split('-')[-1]
        primary_location_market = self.shop_id_cell.format(primary_location_id).get_attribute('data-name')
        del created_ids[core_market_short_name]
        return {primary_location_market.split('shop-id-')[1]: primary_location_id, **created_ids}
