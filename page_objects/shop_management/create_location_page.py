from result import Ok, Err, Result, is_err
from page_objects.base_methods import Locator
from page_objects.shop_management.add_new_location_page import AddLocationPage
from selenium.webdriver.chrome.webdriver import WebDriver


class CreateLocationPage(AddLocationPage):
    username_input = Locator('username_input', arg='//input[@name="username"]')
    password_input = Locator('password_input', arg='//input[@name="password"]')
    password_repeat_input = Locator('password_repeat_input', arg='//input[@name="passwordRepeat"]')
    save_and_next_button = Locator('save_and_next_button', arg='//button[@data-id="button-save-and-next"]')
    finish_button = Locator('finish_button', arg='//button[@data-id="button-finish"]')

    def __init__(self, driver: WebDriver, podio_data: dict):
        super().__init__(driver, podio_data)

    def add_password_and_username(self) -> Result[None, str]:
        try:
            self.wait_for_clickability(self.username_input, 15)
            self.write(self.password_input, self.podio_data['Password'])
            self.write(self.password_repeat_input, self.podio_data['Password'])
            self.write(self.username_input, self.podio_data['Order_Email'])
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_all_fields_in_create_view(self) -> Result[None, str]:
        try:
            self.wait_for_clickability(self.vat_zone_dropdown, 15)
            results = [
                self.add_password_and_username(),
                self.update_all_fields_in_add_view()
            ]
        except Exception as e:
            return self.handle_exception(e)

        errors = "\n".join(result.err_value for result in results if is_err(result))
        if errors:
            return Err(errors)
        return Ok(None)

    def save_create_view(self, values_before_changes: dict) -> Result[dict, str]:
        if self.get_elements(self.finish_button):
            return self.save(values_before_changes, custom_button=self.finish_button)
        return self.save(values_before_changes)
