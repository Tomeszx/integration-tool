import contextlib
import traceback

from result import Ok, Err, Result, is_err
from selenium.webdriver.chrome.webdriver import WebDriver

from api_objects.google_sheet_api import upload_file
from page_objects.base_methods import Locator, BaseMethods

MARKETS_NAMES = {
    "NL": "Netherlands", "DK": "Denmark", "SE": "Sweden", "BE": "Belgium", "FR": "France", "IT": "Italy", "ES": "Spain",
    "DE": "Germany", "PL": "Poland", "UK": "United Kingdom", "FI": "Finland", "CN": "China", "NO": "Norway"
}


class LocationInfoPage(BaseMethods):
    core_location_text = Locator('core_location_text', arg='//*[@data-id="preview-primary-core-platform"]')
    location_id_text = Locator('market_id_text', arg='//*[@data-id="shop-id-{}"]')
    location_name_input = Locator('location_name_input', arg='//input[@name="name"]')
    core_location_dropdown = Locator('core_location_dropdown', arg='//div[@data-id="partner-core-location"]')
    local_currency_dropdown = Locator('local_currency_dropdown', arg='//div[@data-id="localCurrency"]')
    source_language_dropdown = Locator('source_language_dropdown', arg='//div[@data-id="sourceLanguage"]')
    save_and_next_button = Locator('save_and_next_button', arg='//button[@data-id="button-save-and-next"]')

    def __init__(self, driver: WebDriver, data: dict):
        super().__init__(driver)
        self.data = data

    def _get_ids(self, expected_ids: list) -> Result[list, list]:
        new_ids = []
        for shop_id in expected_ids:
            location = shop_id.split("-")[0]
            new_id = self.get_elements(self.location_id_text.__format__(location.replace('UK', 'GB')))
            if new_id and new_id[0].text.isdigit():
                new_ids.append(f"{location}-{new_id[0].text}")

        if len(new_ids) < len(expected_ids):
            return Err(new_ids)
        return Ok(new_ids)

    def add_location_info_and_go_to_next_step(self, core_market: str) -> Result[None, list]:
        try:
            self.wait_for_clickability(self.location_name_input, 15)

            self.write(self.location_name_input, self.data['partner_name'])
            self.select(self.core_location_dropdown, MARKETS_NAMES[core_market])
            self.select(self.local_currency_dropdown, 'EUR')
            self.select(self.source_language_dropdown, 'English')
            self.click(self.save_and_next_button)

            self.wait_for_invisibility(self.location_name_input, 10)
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def wait_for_ids(self, expected_ids: list) -> Result[tuple[None, list], tuple[str, list]]:
        self.open(f'/preview/{self.data["shop_management_id"]}/info')
        self.wait_for_visibility(self.core_location_text, 15)

        core_market = self.get_attribute(self.core_location_text, 'innerText')
        core_market_dict_index = list(MARKETS_NAMES.values()).index(core_market)

        with contextlib.suppress(Exception):
            self.wait_for_visibility(self.location_id_text.__format__(
                list(MARKETS_NAMES)[core_market_dict_index]), 30
            )

        screen_url = upload_file(self.make_screen(' waiting for ids'))
        error_comment = f"Couldn't map all created ids.\nScreenshot: {screen_url}"
        core_id = self.get_elements(self.location_id_text.__format__(list(MARKETS_NAMES)[core_market_dict_index]))
        if not core_id or not core_id[0].text.isdigit():
            return Err((error_comment, []))

        result = self._get_ids(expected_ids)
        if is_err(result):
            return Err((error_comment, result.err_value))
        return Ok((None, result.ok_value))
