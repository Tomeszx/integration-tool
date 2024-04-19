import os
import pycountry

from page_objects.base_methods import BaseMethods, Locator
from phonenumbers import format_number, parse, PhoneNumberFormat
from result import Ok, Err, Result, is_err
from selenium.webdriver.chrome.webdriver import WebDriver
from schwifty import IBAN, bic


BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('/page_objects', '')


class EditLocationPage(BaseMethods):
    location_selector = Locator('market_selector', arg="//button[@role='tab']/span[text()='{}']")
    user_type_dropdown = Locator('user_type_dropdown', arg='//div[@data-id="userType"]')
    activity_dropdown = Locator('activity_dropdown', arg='//div[@data-id="activity"]')
    shop_name_input = Locator('shop_name_input', arg='//input[@name="shopName"]')
    legal_name_input = Locator('legal_name_input', arg='//input[@name="legalName"]')
    order_email_input = Locator('order_email_input', arg='//input[@name="orderEmail"]')
    payment_method_dropdown = Locator('payment_method_dropdown', arg='//div[@data-id="paymentMethod"]')
    bank_account_number_input = Locator('bank_account_number_input', arg='//input[@name="bankAccountNumber"]')
    bank_code_input = Locator('bank_code_input', arg='//input[@name="bankRegistrationNumber"]')
    vat_tax_input = Locator('vat_tax_input', arg='//input[@name="CVR"]')
    shipping_name_input = Locator('shipping_name_input', arg='//input[@name="shippingAddresses.{}.name"]')
    shipping_street_1_input = Locator(
        'shipping_street_1_input', arg='//input[@name="shippingAddresses.{}.street1"]')
    shipping_street_2_input = Locator(
        'shipping_street_2_input', arg='//input[@name="shippingAddresses.{}.street2"]')
    shipping_zip_code_input = Locator(
        'shipping_zip_code_input', arg='//input[@name="shippingAddresses.{}.zipCode"]')
    shipping_city_input = Locator('shipping_city_input', arg='//input[@name="shippingAddresses.{}.city"]')
    shipping_country_dropdown = Locator(
        'shipping_country_dropdown', arg='//div[@data-id="shippingAddresses.{}.country"]')
    shipping_tab_buttons = Locator(
        'shipping_tab_buttons', arg='//button[contains(@data-id, "button-shipping-address-")]')
    shipping_tab_button = Locator('shipping_tab_button', arg='//button[@data-id="button-shipping-address-{}"]')
    shipping_remove_button = Locator(
        'shipping_remove_button', arg='//button[@data-id="button-remove-shipping-address"]')
    shipping_add_button = Locator('shipping_add_button', arg='//button[@data-id="button-add-shipping-address"]')
    contacts_0_email_input = Locator('contacts_0_email_input', arg='//input[@name="contacts.0.email"]')
    contacts_0_name_input = Locator('contacts_0_name_input', arg='//input[@name="contacts.0.name"]')
    contacts_1_email_input = Locator('contacts_1_email_input', arg='//input[@name="contacts.1.email"]')
    contacts_1_name_input = Locator('contacts_1_name_input', arg='//input[@name="contacts.1.name"]')
    contacts_phone_number_input = Locator('contacts_phone_number_input', arg='//input[@name="phoneNumber"]')
    invoicing_country_dropdown = Locator(
        'invoicing_country_dropdown', arg='//div[@data-id="invoicingAddress.country"]')
    invoicing_street_1_input = Locator(
        'invoicing_street_1_input', arg='//input[@name="invoicingAddress.street1"]')
    invoicing_street_2_input = Locator(
        'invoicing_street_2_input', arg='//input[@name="invoicingAddress.street2"]')
    invoicing_zip_code_input = Locator(
        'invoicing_zip_code_input', arg='//input[@name="invoicingAddress.zipCode"]')
    invoicing_city_input = Locator('invoicing_city_input', arg='//input[@name="invoicingAddress.city"]')
    invoicing_emails_input = Locator('invoicing_emails_input', arg='//input[@name="invoicingEmails"]')
    signup_date_input = Locator('signup_date_input', arg='//input[@name="signupDate"]')
    signed_by_input = Locator('signed_by_input', arg='//input[@name="signedBy"]')
    consultant_input = Locator('consultant_input', arg='//input[@name="consultant"]')
    customer_care_input = Locator('customer_care_input', arg='//input[@name="customerCare"]')
    transfer_price_restriction_input = Locator(
        'transfer_price_restriction_input', arg='//input[@name="transferPriceRestriction"]')
    order_distribution_delay_input = Locator(
        'order_distribution_delay_input', arg='//input[@name="orderDistributionDelay"]')
    return_name_input = Locator('return_name_input', arg='//input[@name="returnAddress.name"]')
    return_street_1_input = Locator('return_street_1_input', arg='//input[@name="returnAddress.street1"]')
    return_street_2_input = Locator('return_street_2_input', arg='//input[@name="returnAddress.street2"]')
    return_zip_code_input = Locator('return_zip_code_input', arg='//input[@name="returnAddress.zipCode"]')
    return_city_input = Locator('return_city_input', arg='//input[@name="returnAddress.city"]')
    return_country_dropdown = Locator('return_country_dropdown', arg='//div[@data-id="returnAddress.country"]')
    return_copy_from_shipping_button = Locator(
        'return_copy_from_shipping_button', arg='//button[@data-id="button-copy-first-shipping-address"]')
    subscription_type_dropdown = Locator('subscription_type_dropdown', arg='//div[@data-id="subscriptionType"]')
    reducer_type_dropdown = Locator('reducer_type_dropdown', arg='//div[@data-id="reducerType"]')
    display_tick_box = Locator(
        'display_tick_box', arg='//input[@data-id="featureDisplayshop_management_idAddress"]/..//button')
    shipping_service_tick_box = Locator(
        'shipping_service_tick_box', arg='//input[@data-id="featureshop_management_idShippingService"]/..//button')
    free_shipping_service_tick_box = Locator(
        'free_shipping_service_tick_box', arg='//input[@data-id="featureFreShippingService"]/..//button')
    price_restriction_tick_box = Locator(
        'price_restriction_tick_box', arg='//input[@data-id="featureTransferPriceRestriction"]/..//button')
    distribution_delay_tick_box = Locator(
        'distribution_delay_tick_box', arg='//input[@data-id="featureOrderDistributionDelay"]/..//button')
    save_button = Locator('save_button', arg='//button[@data-id="button-on-save-edit-form"]')
    edit_market_button = Locator('edit_market_button', arg='//button[@data-id="button-location-or-partner-edit"]')
    preview_mode = Locator('preview_mode', arg='//div[@data-component="partner-preview"]')
    edit_view_mode = Locator('edit_view_mode', arg='//div[@data-component="partner-edit"]')

    def __init__(self, driver: WebDriver, podio_data: dict):
        super().__init__(driver)
        self.podio_data = podio_data
        self.location = None

    def open_specific_market(self):
        locator = self.location_selector.__format__(self.location.upper())
        self.wait_for_clickability(locator).click()
        self.get_element(self.edit_market_button).click()

    @staticmethod
    def _get_street(street: str) -> tuple:
        street_1, street_2 = "", ""
        for word in street.replace("\n", " ").split(" "):
            if len(f"{street_1} {word}") <= 30:
                street_1 += f" {word}"
            elif len(f"{street_2} {word}") <= 30:
                street_2 += f" {word}"
        return street_1, street_2

    def _get_bank_account_number(self) -> Result[tuple, str]:
        field_name_podio = 'Bank_Account_Number'
        try:
            return Ok((IBAN(self.podio_data[field_name_podio]).compact, "IBAN/SWIFT"))
        except Exception as e:
            if self.podio_data[field_name_podio].count(";") == 0:
                return Err(f'{e.__class__.__name__} - {str(e).split("Stacktrace:")[0]}')
        try:
            for account in self.podio_data[field_name_podio].replace(" ", "").replace("\n", "").split(";"):
                if self.location in account.split('IBAN:')[0].split(',') and 'IBAN:' in account:
                    iban_number = account.split("IBAN:")[1]
                    return Ok((IBAN(iban_number).compact, "IBAN/SWIFT"))
                elif self.location in account.split('Account:')[0].split(',') and 'Account:' in account:
                    account_number = account.split("Account:")[1]
                    return Ok((account_number, "Bank transfer"))
        except Exception as e:
            return self.handle_exception(e)
        return Err(f'The Iban is not correct. Please check if {self.location} is not missing or if the number is correct')

    def _get_bank_code(self) -> Result[str, str]:
        field_name_podio = 'Bank_Account_Number_-_SWIFT'
        try:
            return Ok(bic.BIC(self.podio_data[field_name_podio]).compact)
        except Exception as e:
            if self.podio_data[field_name_podio].count(";") == 0:
                return Err(str(e).split("Stacktrace:")[0])
        try:
            for account in self.podio_data[field_name_podio].replace(" ", "").replace("\n", "").split(";"):
                if self.location in account.split('SWIFT:')[0].split(',') and 'SWIFT:' in account:
                    bank_code = account.split("SWIFT:")[1]
                    return Ok(bic.BIC(bank_code).compact)
                elif f"{self.location}CODE:" in account:
                    account_number = account.split("CODE:")[1]
                    return Ok(account_number)
        except Exception as e:
            return self.handle_exception(e)
        return Err(f'Issue while updating {field_name_podio} on {self.location} location.')

    def _get_phone_number(self, phone_number: str) -> str:
        try:
            return format_number(parse(phone_number), PhoneNumberFormat.E164)
        except Exception:
            return format_number(parse(phone_number, self.podio_data['Home_Market']), PhoneNumberFormat.E164)

    def _parse_shipping_locations(self, shipping_field_name: str) -> Result[list, str]:
        try:
            data = []
            for address in self.podio_data[shipping_field_name].replace("\n", "").split(";"):
                if address.replace(" ", "") == "":
                    continue
                country_code = address.split('CountryCode=')[1].split('|')[0]
                data.append({
                    'Shipping_Address_-_Country': pycountry.countries.get(alpha_2=country_code).name,
                    'Shipping_Address_-_City': address.split('City=')[1].split('|')[0],
                    'Shipping_Address_-_Street': address.split('Street=')[1].split('|')[0],
                    'partner_name': address.split('Name=')[1].split('|')[0],
                    'Shipping_Address_-_Zip_code': address.split('Zipcode=')[1].split('|')[0]
                })
            return Ok(data)
        except Exception as e:
            return self.handle_exception(e)

    def _delete_all_additional_shipping_locations(self) -> Result[None, str]:
        try:
            for _ in self.get_elements(self.shipping_tab_buttons)[1:]:
                last_tab_index = len(self.get_elements(self.shipping_tab_buttons)) - 1

                self.click(self.shipping_tab_button.__format__(str(last_tab_index)))
                self.click(self.shipping_remove_button)
                self.wait_for_invisibility(self.shipping_tab_button.__format__(str(last_tab_index)), 5)
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def _get_shipping_fields_locators(self) -> dict:
        return {
            'shipping_name_input': self.shipping_name_input,
            'shipping_street_1_input': self.shipping_street_1_input,
            'shipping_street_2_input': self.shipping_street_2_input,
            'shipping_city_input': self.shipping_city_input,
            'shipping_zip_code_input': self.shipping_zip_code_input,
            'shipping_country_dropdown': Locator(
                'shipping_country_dropdown',
                self.shipping_country_dropdown[0], f'{self.shipping_country_dropdown[1]}/button/span'
            )
        }

    def _get_shipping_values(self) -> dict:
        data = {}
        for i, button in enumerate(self.get_elements(self.shipping_tab_buttons)):
            for name, locator in self._get_shipping_fields_locators().items():
                button.click()
                self.wait_for_visibility(locator.__format__(str(i)))
                if 'input' in name:
                    data[f'{name} ~tab-{i}'] = self.get_attribute(locator.__format__(str(i)), 'value')
                else:
                    data[f'{name} ~tab-{i}'] = self.get_attribute(locator.__format__(str(i)), 'innerText')
        return data

    def update_name_section(self) -> Result[None, str]:
        try:
            self.write(self.shop_name_input, self.podio_data['partner_name'])
            self.write(self.legal_name_input, self.podio_data['Legal_Name'])
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_order_email(self) -> Result[None, str]:
        if len(self.podio_data['Order_Email']) > 1:
            return Err("The Order Email could be the only one in Podio.")
        try:
            self.write(self.order_email_input, self.podio_data['Order_Email'])
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_vat_tax_number(self) -> Result[None, str]:
        try:
            self.write(self.vat_tax_input, self.podio_data['VAT_TAX_Number'])
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_price_restriction(self) -> Result[None, str]:
        try:
            self.check(self.price_restriction_tick_box, True)
            self.wait_for_clickability(self.transfer_price_restriction_input, 3)
            self.write(self.transfer_price_restriction_input, self.podio_data.get('Transfer_price_restriction_%', '50'))
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_order_distribution_delay(self) -> Result[None, str]:
        try:
            is_checked = len(self.podio_data.get('Order_distribution_delay_(min)', '')) > 0
            self.check(self.distribution_delay_tick_box, is_checked)
            if is_checked:
                self.wait_for_clickability(self.order_distribution_delay_input, 3)
                self.write(self.order_distribution_delay_input, self.podio_data.get('Order_distribution_delay_(min)', ''))
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_date_of_signing(self) -> Result[None, str]:
        try:
            full_date = str(self.podio_data["Date_of_signing"][0].date())
            for date_part in reversed(full_date.split("-")):
                self.write(self.signup_date_input, date_part)
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_status(self) -> Result[None, str]:
        try:
            if "offline" in self.podio_data['Status_on_Admin'] or "Temp Closed" in self.podio_data['Status_on_Admin']:
                self.select(self.activity_dropdown, "Temp. Closed")
            elif "Churn Closed" in self.podio_data['Status_on_Admin']:
                self.select(self.activity_dropdown, "Closed")
            elif "Active" in self.podio_data['Status_on_Admin'] or "online" in self.podio_data['Status_on_Admin']:
                self.select(self.activity_dropdown, "Full")
            else:
                return Err(f'Missing status option for {self.podio_data["Status_on_Admin"]}.')
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_shipping_agreement_section(self) -> Result[None, str]:
        try:
            if "FREE" in self.podio_data['Shipping_Agreement']:
                self.check(self.shipping_service_tick_box, True)
                self.check(self.free_shipping_service_tick_box, True)
            elif self.podio_data['Shipping_Agreement'] == "Yes":
                self.check(self.shipping_service_tick_box, True)
                self.check(self.free_shipping_service_tick_box, False)
            else:
                self.check(self.shipping_service_tick_box, False)
                self.check(self.free_shipping_service_tick_box, False)
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_bank_account_section(self) -> Result[None, str]:
        bank_account = self._get_bank_account_number()
        if is_err(bank_account):
            return bank_account
        bank_code = self._get_bank_code()
        if is_err(bank_account):
            return bank_account

        try:
            self.select(self.payment_method_dropdown, bank_account.ok_value[1])
            self.wait_for_clickability(self.bank_account_number_input)
            self.write(self.bank_account_number_input, bank_account.ok_value[0])
            self.write(self.bank_code_input, bank_code.ok_value)
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_shipping_section(self, index: int, data: dict, s_type='shipping') -> Result[None, str]:
        my_object = EditLocationPage.__dict__
        try:
            if self.get_elements(self.shipping_tab_buttons):
                self.click(self.shipping_tab_button.__format__(index))

            self.select(my_object[f'{s_type}_country_dropdown'].__format__(index), data['Shipping_Address_-_Country'])
            self.write(my_object[f'{s_type}_name_input'].__format__(index), data['partner_name'])
            self.write(my_object[f'{s_type}_city_input'].__format__(index), data['Shipping_Address_-_City'])
            self.write(my_object[f'{s_type}_zip_code_input'].__format__(index), data['Shipping_Address_-_Zip_code'])
            street = self._get_street(data['Shipping_Address_-_Street'])
            self.write(my_object[f'{s_type}_street_1_input'].__format__(index), street[0])
            self.write(my_object[f'{s_type}_street_2_input'].__format__(index), street[1])
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_invoicing_section(self) -> Result[None, str]:
        try:
            self.select(self.invoicing_country_dropdown, self.podio_data['Invoicing_Address_-_Country'])
            self.write(self.invoicing_zip_code_input, self.podio_data['Invoicing_Address_-_Zipcode'])
            self.write(self.invoicing_city_input, self.podio_data['Invoicing_Address_-_City'])
            self.write(self.invoicing_emails_input, ";".join(self.podio_data['Invoicing_Emails']))
            street = self._get_street(self.podio_data['Invoicing_Address_-_Street'])
            self.write(self.invoicing_street_1_input, street[0])
            self.write(self.invoicing_street_2_input, street[1])
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_contact_person_section(self) -> Result[None, str]:
        try:
            self.write(self.contacts_0_name_input, self.podio_data['Contact_person_1_-_name_&_surname'])
            self.write(self.contacts_0_email_input, self.podio_data['Contact_person_-_emails'][0])
            shop_phone_number = self.podio_data['Shop_phone_number']
            converted_number = self._get_phone_number(shop_phone_number)
            self.write(self.contacts_phone_number_input, converted_number)
            if len(self.podio_data['Contact_person_-_emails']) > 1:
                name = 'Contact_person_{}_-_name_&_surname'
                contact_person_2 = self.podio_data.get(name.format(2), self.podio_data[name.format(1)])
                self.write(self.contacts_1_name_input, contact_person_2)
                self.write(self.contacts_1_email_input, self.podio_data['Contact_person_-_emails'][1])
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def add_additional_shipping_locations(self) -> Result[None, str]:
        result = self._delete_all_additional_shipping_locations()
        if is_err(result):
            return result

        try:
            locations = self._parse_shipping_locations('Additional_shipping_locations_-_Sender')
            if is_err(locations):
                return locations

            for index, location in enumerate(locations.ok_value, 1):
                self.click(self.shipping_add_button)
                update_result = self.update_shipping_section(index, location)
                if is_err(update_result):
                    return update_result
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def add_return_shipping_locations(self, copy_from_shipping_if_none=False) -> Result[None, str]:
        try:
            if not self.podio_data.get('Return_address') and copy_from_shipping_if_none:
                self.wait_for_clickability(self.return_copy_from_shipping_button).click()
                return Ok(None)

            locations = self._parse_shipping_locations('Return_address')
            if is_err(locations):
                return locations

            update_result = self.update_shipping_section(0, locations.ok_value[0], 'return')
            if is_err(update_result):
                return update_result
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_other_fields(self) -> Result[None, str]:
        try:
            shop_type = 'Brand' if self.podio_data['partner_type'] == 'Brands' else 'Shop'
            self.select(self.user_type_dropdown, shop_type)
            self.write(self.signed_by_input, self.podio_data['Signed_by'][0]['name'])
            self.write(self.consultant_input, self.podio_data['Signed_by'][0]['name'])
            self.write(self.customer_care_input, self.podio_data['Onboard_Responsible'][0]['name'])
            self.select(self.subscription_type_dropdown, 'Standard')
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_contact_and_invoicing(self) -> Result[None, str]:
        results = [
            self.update_contact_person_section(),
            self.update_invoicing_section()
        ]
        
        errors = "\n".join(result.err_value for result in results if is_err(result))
        if errors:
            return Err(errors)
        return Ok(None)

    def update_reducer_type(self, reducer_type: str) -> Result[None, str]:
        try:
            self.select(self.reducer_type_dropdown, reducer_type)
        except Exception as e:
            return self.handle_exception(e)
        return Ok(None)

    def update_all_fields_in_edit_view(self) -> Result[None, str]:
        results = [
            self.update_status(),
            self.update_order_email(),
            self.update_other_fields(),
            self.update_name_section(),
            self.update_vat_tax_number(),
            self.update_date_of_signing(),
            self.update_invoicing_section(),
            self.update_price_restriction(),
            self.update_bank_account_section(),
            self.update_contact_person_section(),
            self.update_order_distribution_delay(),
            self.update_shipping_agreement_section(),
            self.update_shipping_section(0, self.podio_data),
            self.add_return_shipping_locations(copy_from_shipping_if_none=True)
        ]
        if 'Additional_shipping_locations_-_Sender' in self.podio_data:
            results.append(
                self.add_additional_shipping_locations(),
            )
        errors = "\n".join(result.err_value for result in results if is_err(result))
        if errors:
            return Err(errors)
        return Ok(None)

    def get_all_values(self, url: str) -> dict:
        self.driver.get(url)
        self.wait_for_clickability(self.shop_name_input, 15)

        data = {}
        locators = filter(lambda locator: isinstance(locator[1], Locator), EditLocationPage.__dict__.items())
        for name, locator in locators:
            if 'shipping' in name and 'button' not in name and 'tick_box' not in name:
                continue
            elif 'input' in name:
                data[name] = self.get_attribute(locator, 'value')
            elif 'dropdown' in name:
                locator = Locator(locator.name, locator[0], f'{locator[1]}/button/span')
                data[name] = self.get_attribute(locator, 'innerText')
            elif 'tick_box' in name:
                data[name] = self.get_attribute(locator, 'aria-checked')
        data |= self._get_shipping_values()
        return data

    def save(self, values_before: dict, custom_button=None) -> Result[str, str]:
        try:
            current_url = self.driver.current_url
            self.wait_for_clickability(custom_button or self.save_button, 5).click()
            self.wait_for_visibility(self.preview_mode, 15)

            data = self.get_all_values(current_url)
            changes = ""
            for field_name, current_value in data.items():
                if values_before.get(field_name) != current_value:
                    changes += f"\n\n{field_name}:\n---\n\n >[{values_before.get(field_name, '')}]-->[{current_value}]"
        except Exception as e:
            return self.handle_exception(e)
        return Ok(changes)
