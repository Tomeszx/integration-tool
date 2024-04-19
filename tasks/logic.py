#!venv/bin/python3.9
import re

from api_objects.podio_api import get_access_token, Podio
from page_objects.shop_management.edit_location_page import EditLocationPage
from page_objects.shop_management.login_page import LoginPage
from result import is_err
from selenium.webdriver.chrome.webdriver import WebDriver

from tasks.context import Context
from tasks.shop_management import add_new_locations, create_core_location, other_tasks


class Task:
    additional_shipping_locations = EditLocationPage.add_additional_shipping_locations
    shipping_agreement = EditLocationPage.update_shipping_agreement_section
    distribution_delay = EditLocationPage.update_order_distribution_delay
    shop_phone_number = EditLocationPage.update_contact_person_section
    return_address = EditLocationPage.add_return_shipping_locations
    invoicing_email = EditLocationPage.update_contact_and_invoicing
    contact_person = EditLocationPage.update_contact_person_section
    address_email = EditLocationPage.update_contact_and_invoicing
    price_restriction = EditLocationPage.update_price_restriction
    all_fields = EditLocationPage.update_all_fields_in_edit_view
    name_field_change = EditLocationPage.update_name_section
    iban = EditLocationPage.update_bank_account_section
    order_email = EditLocationPage.update_order_email
    status_on_admin = EditLocationPage.update_status
    vat_tax = EditLocationPage.update_vat_tax_number
    create_core = create_core_location.run
    other_markets = add_new_locations.run

    def __init__(self, context: Context):
        self.additional_shipping_locations = context.edit_page.add_additional_shipping_locations
        self.shipping_agreement = context.edit_page.update_shipping_agreement_section
        self.distribution_delay = context.edit_page.update_order_distribution_delay
        self.shop_phone_number = context.edit_page.update_contact_person_section
        self.return_address = context.edit_page.add_return_shipping_locations
        self.invoicing_email = context.edit_page.update_contact_and_invoicing
        self.contact_person = context.edit_page.update_contact_person_section
        self.address_email = context.edit_page.update_contact_and_invoicing
        self.price_restriction = context.edit_page.update_price_restriction
        self.all_fields = context.edit_page.update_all_fields_in_edit_view
        self.name_field_change = context.edit_page.update_name_section
        self.iban = context.edit_page.update_bank_account_section
        self.order_email = context.edit_page.update_order_email
        self.status_on_admin = context.edit_page.update_status
        self.vat_tax = context.edit_page.update_vat_tax_number
        self.create_core = create_core_location.run
        self.other_markets = add_new_locations.run

    def __getitem__(self, item):
        title = re.sub('[/\s]', '_', item).lower()
        return self.__dict__[title]


class TasksManager:
    def __init__(self, comment_frequency: int, user_inputs: dict, chrome_options, driver: WebDriver):
        self.driver = driver
        self.tokens = get_access_token()
        self.podio = Podio(self.tokens, user_inputs)
        self.comment_frequency = comment_frequency
        self.user_inputs = user_inputs
        self.chrome_options = chrome_options

    def _manage_tasks(self, context: Context, task: dict) -> None:
        task_title = re.sub('[/\s]', '_', task['part_title']).lower()
        function = Task(context)[task['part_title']]
        if task_title == 'create_core':
            result = function(context)
        elif task_title == 'other_markets':
            result = function(context)
        else:
            result = other_tasks.run(context, function)

        if is_err(result):
            comments = context.podio_data['comments']
            print(context.podio.add_error_comment(result.err_value, task, comments, self.comment_frequency))
        else:
            context.podio.complete_task(task['task_id'])
            print(context.podio.add_comment(result.ok_value, task))

    def perform_data(self, tasks_fields: dict) -> None:
        tasks_array = self.podio.prepare_tasks(tasks_fields)
        LoginPage(self.driver, self.user_inputs).login()
        for i, task in enumerate(tasks_array[::-1], 1):
            print(f"\n{'':^60}[{i}/{len(tasks_array)}] {task['partner_name']} {task['task_text']}")

            context = Context(self.driver, self.podio, task)

            result = context.podio.prepare_data(context.podio_data, task, tasks_fields)
            if is_err(result):
                comments = context.podio_data['comments']
                print(context.podio.add_error_comment(result.err_value, task, comments, self.comment_frequency))
                continue

            self._manage_tasks(context, task)
