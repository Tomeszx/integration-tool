import os

from datetime import datetime
from result import Result, Err, Ok
from retry import retry
from apiObjects.google_sheet_api import upload_file
from model.address import Address, ShippingAddress, ShippingAddresses, ReturnAddress
from model.bank_info import Iban, BankCode
from model.contact import Contact
from model.elements.button import Button
from model.elements.checkbox import Checkbox
from model.elements.dropdown import Dropdown
from model.elements.element import Element
from model.elements.input import Input
from model.podio_item import PartnerFieldsPodio
from pageObjects.base_methods import BaseMethods
from selenium.webdriver.chrome.webdriver import WebDriver


BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('/pageObjects', '')


class EditMarketPage(BaseMethods):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)

        self.market_selector = Button(driver, "//button[@role='tab']/span[text()='{}']/..")
        self.user_type_dropdown = Dropdown(driver, '//div[@data-name="userType"]/button')
        self.activity_dropdown = Dropdown(driver, '//div[@data-name="activity"]/button')
        self.shop_name_input = Input(driver, '//input[@name="shopName"]')
        self.legal_name_input = Input(driver, '//input[@name="legalName"]')
        self.order_email_input = Input(driver, '//input[@name="orderEmail"]')
        self.payment_method_dropdown = Dropdown(driver, '//div[@data-name="paymentMethod"]/button')
        self.bank_account_number_input = Input(driver, '//input[@name="bankAccountNumber"]')
        self.bank_code_input = Input(driver, '//input[@name="bankRegistrationNumber"]')
        self.vat_tax_input = Input(driver, '//input[@name="CVR"]')
        self.shipping_name_input = Input(driver, '//input[@name="shippingAddresses.{}.name"]')
        self.shipping_street_1_input = Input(driver, '//input[@name="shippingAddresses.{}.street1"]')
        self.shipping_street_2_input = Input(driver, '//input[@name="shippingAddresses.{}.street2"]')
        self.shipping_zip_code_input = Input(driver, '//input[@name="shippingAddresses.{}.zipCode"]')
        self.shipping_city_input = Input(driver, '//input[@name="shippingAddresses.{}.city"]')
        self.shipping_country_dropdown = Dropdown(driver, '//div[@data-name="shippingAddresses.{}.country"]/button')
        self.shipping_tab_buttons = Button(driver, '//button[contains(@data-name, "button-shipping-address-")]')
        self.shipping_tab_button = Button(driver, '//button[@data-name="button-shipping-address-{}"]')
        self.shipping_remove_button = Button(driver, '//button[@data-name="button-remove-shipping-address"]')
        self.shipping_add_button = Button(driver, '//button[@data-name="button-add-shipping-address"]')
        self.contacts_0_email_input = Input(driver, '//input[@name="contacts.0.email"]')
        self.contacts_0_name_input = Input(driver, '//input[@name="contacts.0.name"]')
        self.contacts_1_email_input = Input(driver, '//input[@name="contacts.1.email"]')
        self.contacts_1_name_input = Input(driver, '//input[@name="contacts.1.name"]')
        self.contacts_phone_number_input = Input(driver, '//input[@name="phoneNumber"]')
        self.invoicing_country_dropdown = Dropdown(driver, '//div[@data-name="invoicingAddress.country"]/button')
        self.invoicing_street_1_input = Input(driver, '//input[@name="invoicingAddress.street1"]')
        self.invoicing_street_2_input = Input(driver, '//input[@name="invoicingAddress.street2"]')
        self.invoicing_zip_code_input = Input(driver, '//input[@name="invoicingAddress.zipCode"]')
        self.invoicing_city_input = Input(driver, '//input[@name="invoicingAddress.city"]')
        self.invoicing_emails_input = Input(driver, '//input[@name="invoicingEmails"]')
        self.signup_date_input = Input(driver, '//input[@name="signupDate"]')
        self.signed_by_input = Input(driver, '//input[@name="signedBy"]')
        self.consultant_input = Input(driver, '//input[@name="consultant"]')
        self.customer_care_input = Input(driver, '//input[@name="customerCare"]')
        self.transfer_price_restriction_input = Input(driver, '//input[@name="transferPriceRestriction"]')
        self.commission_input = Input(driver, '//input[@name="commission"]')
        self.order_distribution_delay_input = Input(driver, '//input[@name="orderDistributionDelay"]')
        self.return_name_input = Input(driver, '//input[@name="returnAddress.name"]')
        self.return_street_1_input = Input(driver, '//input[@name="returnAddress.street1"]')
        self.return_street_2_input = Input(driver, '//input[@name="returnAddress.street2"]')
        self.return_zip_code_input = Input(driver, '//input[@name="returnAddress.zipCode"]')
        self.return_city_input = Input(driver, '//input[@name="returnAddress.city"]')
        self.return_country_dropdown = Dropdown(driver, '//div[@data-name="returnAddress.country"]/button')
        self.return_copy_from_shipping_button = Button(driver, '//button[@data-name="button-copy-first-shipping-address"]')
        self.subscription_type_dropdown = Dropdown(driver, '//div[@data-name="subscriptionType"]/button')
        self.reducer_type_dropdown = Dropdown(driver, '//div[@data-name="reducerType"]/button')
        self.display_tick_box = Checkbox(driver, '//input[@data-name="featureDisplayAddress"]/..//button')
        self.shipping_service_tick_box = Checkbox(driver, '//input[@data-name="featureShippingService"]/..//button')
        self.free_shipping_service_tick_box = Checkbox(driver, '//input[@data-name="featureFreeShippingService"]/..//button')
        self.price_restriction_tick_box = Checkbox(driver, '//input[@data-name="featureTransferPriceRestriction"]/..//button')
        self.distribution_delay_tick_box = Checkbox(driver, '//input[@data-name="featureOrderDistributionDelay"]/..//button')
        self.save_button = Button(driver, '//button[@data-name="button-on-save-edit-form"]')
        self.edit_market_button = Button(driver, '//button[@data-name="button-market-or-partner-edit"]')
        self.preview_mode = Element(driver, '//div[@data-component="partner-preview"]')
        self.edit_view_mode = Element(driver, '//div[@data-component="partner-edit"]')
        self.front_errors = Element(driver, '//p[contains(@data-name, "error")]')
        self.popup_error_text = Element(driver, '//div[@id="marketEditErrorModal"]/div/p')
        self.error_popup_cancel_button = Button(driver, '//button[@data-name="marketEditErrorModal-cancel"]')

    def open_specific_market(self, market: str):
        converted_market = market.replace('UK', 'GB').replace('SHWRM', 'PL')
        self.market_selector.format(converted_market.upper()).click()

    def go_to_form_view(self):
        self.edit_market_button.click(timeout=2)

    def update_name_section(self, shop_name: str, legal_name: str) -> None:
        self.shop_name_input.value = shop_name
        self.legal_name_input.value = legal_name

    def update_order_email(self, order_email: str) -> None:
        self.order_email_input.value = order_email

    def update_commission(self, value: int) -> None:
        self.commission_input.value = value

    def update_vat_number(self, vat_number: str) -> None:
        self.vat_tax_input.value = vat_number

    def update_price_restriction(self, price_percent: int) -> None:
        if price_percent > 0:
            self.price_restriction_tick_box.check()
            self.transfer_price_restriction_input.wait_for_clickability(timeout=2)
            self.transfer_price_restriction_input.value = price_percent
        else:
            self.price_restriction_tick_box.uncheck()

    def update_order_distribution_delay(self, delay_in_minutes: int) -> None:
        if delay_in_minutes > 0:
            self.distribution_delay_tick_box.check()
            self.order_distribution_delay_input.wait_for_clickability(timeout=2)
            self.order_distribution_delay_input.value = delay_in_minutes
        else:
            self.distribution_delay_tick_box.uncheck()

    def update_date_of_signing(self, date: datetime.date) -> None:
        self.signup_date_input.value = date.day
        self.signup_date_input.value = date.month
        self.signup_date_input.value = date.year

    def update_status(self, status: str) -> None:
        if "offline" in status or "Temp Closed" in status:
            self.activity_dropdown.open().select_option("Temp. Closed")
        elif "Churn Closed" in status:
            self.activity_dropdown.open().select_option("Closed")
        elif "Active" in status or "online" in status:
            self.activity_dropdown.open().select_option("Full")
        else:
            raise ValueError(f'Missing status option for {status}.')

    def update_shipping_agreement_section(self, shipping_type: str) -> None:
        if "FREE" in shipping_type:
            self.shipping_service_tick_box.check()
            self.free_shipping_service_tick_box.check()
        elif shipping_type == "Yes":
            self.shipping_service_tick_box.check()
            self.free_shipping_service_tick_box.uncheck()
        else:
            self.shipping_service_tick_box.uncheck()
            self.free_shipping_service_tick_box.uncheck()

    def update_bank_account_section(self, bank_number: Iban, bank_code: BankCode) -> None:
        self.payment_method_dropdown.open().select_option(bank_number.type)
        self.bank_account_number_input.wait_for_clickability(timeout=2)
        self.bank_account_number_input.value = bank_number.number
        self.bank_code_input.value = bank_code.number

    def update_shipping_section(self, index: int, address: ShippingAddress) -> None:
        name_elem = self.shipping_name_input.format(index)
        name_elem.wait_for_clickability(timeout=2)
        name_elem.value = address.name

        self.shipping_city_input.format(index).value = address.city
        self.shipping_zip_code_input.format(index).value = address.zip
        self.shipping_street_1_input.format(index).value = address.street_1
        self.shipping_street_2_input.format(index).value = address.street_2
        self.shipping_country_dropdown.format(index).open().select_option(address.country)

    def update_invoicing_section(self, address: Address, emails: list[str]) -> None:
        self.invoicing_country_dropdown.open().select_option(address.country)
        self.invoicing_zip_code_input.value = address.zip
        self.invoicing_city_input.value = address.city
        self.invoicing_emails_input.value = ";".join(emails)
        self.invoicing_street_1_input.value = address.street_1
        self.invoicing_street_2_input.value = address.street_2

    def update_contact_person_section(self, contact: Contact) -> None:
        self.contacts_0_name_input.value = contact.name_1
        self.contacts_0_email_input.value = contact.email_1
        self.contacts_phone_number_input.value = contact.phone
        if contact.email_2:
            self.contacts_1_name_input.value = contact.name_2 or contact.name_1
            self.contacts_1_email_input.value = contact.email_2

    def delete_all_additional_shipping_locations(self) -> None:
        for _ in self.shipping_tab_buttons.get_elements()[1:]:
            last_tab_index = len(self.shipping_tab_buttons.get_elements()) - 1
            self.shipping_tab_button.format(str(last_tab_index)).click()
            self.shipping_remove_button.click()
            self.shipping_tab_button.format(str(last_tab_index)).wait_for_invisibility(timeout=2)

    def add_additional_shipping_locations(self, addresses: ShippingAddresses) -> None:
        for i, address in enumerate(addresses.data, 1):
            self.shipping_add_button.click()
            tab_button = self.shipping_tab_button.format(i)
            tab_button.wait_for_visibility(timeout=2).click()
            self.update_shipping_section(i, address)

    def copy_return_address_from_shipping(self) -> None:
        self.return_copy_from_shipping_button.click(timeout=2)

    def add_return_shipping_location(self, address: ReturnAddress) -> None:
        self.return_name_input.wait_for_clickability(timeout=2)

        self.return_name_input.value = address.data.name
        self.return_city_input.value = address.data.city
        self.return_zip_code_input.value = address.data.zip
        self.return_street_1_input.value = address.data.street_1
        self.return_street_2_input.value = address.data.street_2
        self.return_country_dropdown.open().select_option(address.data.country)

    def update_other_fields(self, partner_type: str, signed_by: str, onboard_by: str) -> None:
        shop_type = 'Brand' if partner_type == 'Brands' else 'Shop'
        self.user_type_dropdown.open().select_option(shop_type)
        self.signed_by_input.value = signed_by
        self.consultant_input.value = signed_by
        self.customer_care_input.value = onboard_by
        self.subscription_type_dropdown.open().select_option('Standard')

    def update_reducer_type(self, reducer_type: str) -> None:
        self.reducer_type_dropdown.open().select_option(reducer_type)

    def update_all_fields_in_edit_view(self, market: str, fields: PartnerFieldsPodio) -> None:
        self.update_name_section(fields.boutique_name, fields.legal_name)
        self.update_status(fields.status)
        self.update_order_email(fields.order_email[0])
        self.update_vat_number(fields.vat_number)
        self.update_date_of_signing(fields.date_of_signing)
        self.update_shipping_agreement_section(fields.shipping_agreement)
        self.update_bank_account_section(Iban(market, fields.iban), BankCode(market, fields.bank_code))
        self.update_commission(fields.pure_commission)
        self.update_price_restriction(fields.price_restriction)
        self.update_order_distribution_delay(fields.order_delay)
        self.update_other_fields(fields.partner_type, fields.signed_by[0], fields.onboard_responsible[0])

        i_zip = fields.invoicing_zip_code
        invoicing_address = Address(fields.invoicing_street, fields.invoicing_city, i_zip, fields.invoicing_country)
        self.update_invoicing_section(invoicing_address, fields.invoicing_email)

        contact = Contact(fields.contact_person, fields.contact_email, fields.contact_phone, fields.home_market)
        self.update_contact_person_section(contact)

        ship_details = fields.shipping_street, fields.shipping_city, fields.shipping_zip_code, fields.shipping_country
        ship_address = ShippingAddress(fields.boutique_name, *ship_details)
        self.update_shipping_section(0, ship_address)

        if fields.additional_shipping_locations:
            self.delete_all_additional_shipping_locations()
            self.add_additional_shipping_locations(fields.additional_shipping_locations)

        if fields.return_address:
            self.add_return_shipping_location(fields.return_address)
        else:
            self.copy_return_address_from_shipping()

    def _get_shipping_values(self) -> dict:
        data = {}
        tabs = self.shipping_tab_buttons.get_elements()
        if not tabs:
            tabs = [None]
        for i, button in enumerate(tabs):
            if button:
                button.click()

            shipping_name_elem = self.shipping_name_input.format(str(i))
            shipping_name_elem.wait_for_presence(timeout=2)

            data[f'name ~tab-{i}'] = shipping_name_elem.value
            data[f'city ~tab-{i}'] = self.shipping_city_input.format(str(i)).value
            data[f'zip-code ~tab-{i}'] = self.shipping_zip_code_input.format(str(i)).value
            data[f'street-1 ~tab-{i}'] = self.shipping_street_1_input.format(str(i)).value
            data[f'street-2 ~tab-{i}'] = self.shipping_street_2_input.format(str(i)).value
            data[f'country ~tab-{i}'] = self.shipping_country_dropdown.format(str(i)).selected_option
        return data

    def get_all_values(self, url: str) -> dict:
        self.driver.get(url)
        self.shop_name_input.wait_for_clickability(timeout=5)

        data = {}
        locators = list(filter(
            lambda element: isinstance(element[1], (Button, Input, Dropdown, Checkbox, Element)), self.__dict__.items()
        ))
        for name, element in locators:
            if 'shipping' in name:
                continue
            elif isinstance(element, Input):
                data[name] = element.value
            elif isinstance(element, Dropdown):
                data[name] = element.selected_option
            elif isinstance(element, Checkbox):
                data[name] = element.is_checked
        return {**data, **self._get_shipping_values()}

    def get_differences_between_values(self, values_before: dict) -> str:
        self.edit_market_button.click(timeout=2)
        self.edit_view_mode.wait_for_presence(timeout=3)

        current_url = self.driver.current_url
        data = self.get_all_values(current_url)
        changes = ""
        for field_name, current_value in data.items():
            if values_before.get(field_name) != current_value:
                changes += f"\n\n{field_name}:\n---\n\n >[{values_before.get(field_name, '')}]-->[{current_value}]"
        if not changes:
            changes += "Nothing was changed. Data in PaMS are the same.\n\n"
        return changes

    @retry(tries=3, delay=0.5)
    def save(self) -> Result[None, str]:
        if not self.check_if_the_form_is_saved():
            self.save_button.click(timeout=3)
            self.wait_for_ready_state(timeout=5)

        if not self.check_if_the_form_is_saved():
            errors = self.get_errors()
            if not errors:
                raise Exception('the form was not saved properly and there are no errors')
            return Err(errors)
        return Ok(None)

    def check_if_the_form_is_saved(self) -> bool:
        if self.preview_mode.is_present(0.1):
            return True
        return False

    def get_errors(self) -> str:
        response = ""
        if self.front_errors.is_present(timeout=0.3):
            error_message = "\n".join([i.get_attribute("data-name") for i in self.front_errors.get_elements()])
            for line in error_message.split("\n"):
                response += "`Incorrect field [" + f"]`\n --- \n\n > ".join(line.split("error")) + "\n\n"
        elif self.popup_error_text.is_present(timeout=0.3):
            details = self.popup_error_text.get_elements()[-1]
            response = f"`Error`\n --- \n\n > {details.text}"
            self.error_popup_cancel_button.click(timeout=2)

        if response:
            screen = self.make_screen(f'proxy error')
            screen_url = upload_file(screen)
            response = f"Screenshot: {screen_url}\n{response}"
        return response
