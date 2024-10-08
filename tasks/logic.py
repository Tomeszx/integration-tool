#!venv/bin/python3.9
from functools import partial

from apiObjects.podio_api import get_access_token, Podio
from common.exceptions.handler import handle_exception
from model.address import Address
from model.contact import Contact
from model.podio_item import PartnerFieldsPodio, PdfFile
from model.podio_tasks import PodioTask
from pageObjects.pams.login_page import LoginPage
from result import is_err, is_ok, Result, Ok, Err
from selenium.webdriver.chrome.webdriver import WebDriver
from tasks.context import Context
from tasks.pams import create_core_market, add_new_markets, all_fields, other_tasks, iban
from utilites.config_parser import get_required_fields_per_task


def transform_result_into_comment(task: str, error_comments: dict, success_comments: dict) -> Result[str, str]:
    comment = f"Task: {task}\n\n"
    for comment_to_add, markets in success_comments.items():
        comment += f"# The msg from markets [{', '.join(markets)}]:\n{comment_to_add}\n\n"
    if error_comments:
        comment += f"There was an issue.\n\n" \
                   f" --- \nTo handle this error please contact with us.\n\n --- "
        for error_comment, markets in error_comments.items():
            comment += f"\n\n# The msg from markets [{', '.join(markets)}]\n{error_comment}"
        return Err(comment)
    return Ok(comment)


def process_output(results: list, task: str) -> Result[str, str]:
    error_comments, success_comments = {}, {}
    for result in results:
        try:
            if is_err(result[1]) and result[1].value not in error_comments:
                error_comments[result[1].value] = [result[0]]
            elif is_err(result[1]):
                error_comments[result[1].value].append(result[0])
            elif result[1].value not in success_comments:
                success_comments[result[1].value] = [result[0]]
            else:
                success_comments[result[1].value].append(result[0])
        except AttributeError as e:
            raise AttributeError(f'{type(result)=} {result=}') from e
    return transform_result_into_comment(task, error_comments, success_comments)



class TasksManager:
    def __init__(self, comment_frequency: int, user_inputs: dict, chrome_options, driver: WebDriver):
        self.driver = driver
        self.tokens = get_access_token()
        self.podio = Podio(self.tokens, user_inputs)
        self.comment_frequency = comment_frequency
        self.user_inputs = user_inputs
        self.chrome_options = chrome_options

    def _manage_tasks(
            self, context: Context, task: PodioTask, fields: PartnerFieldsPodio, pdf_file: PdfFile
    ) -> Result[str, str]:

        required_fields = get_required_fields_per_task()[task.short_title]
        check_result = fields.check_required_fields(required_fields)
        if is_err(check_result):
            return check_result
        if 'Create core' == task.short_title and not pdf_file:
            return Err("PDF contract is not attached to the Podio.")

        results = []

        match task.short_title:
            case 'Create core':
                results = create_core_market.run(context, fields)
            case 'Other markets':
                results = add_new_markets.run(context, fields)
            case 'all fields':
                results = all_fields.run(context, fields)
            case 'IBAN':
                results = iban.run(context, fields)
            case 'Shop phone number' | 'Contact person':
                contact = Contact(fields.contact_person, fields.contact_email, fields.contact_phone, fields.home_market)
                partial_func = partial(context.edit_page.update_contact_person_section, contact)
                results = other_tasks.run(context, fields, partial_func)
            case 'Invoicing Email' | 'Address/email':
                i_zip, i_country = fields.invoicing_zip_code, fields.invoicing_country
                address = Address(fields.invoicing_street, fields.invoicing_city, i_zip, i_country)
                partial_func = partial(context.edit_page.update_invoicing_section, address, fields.invoicing_email)
                results = other_tasks.run(context, fields, partial_func)
            case 'Status on Admin':
                partial_func = partial(context.edit_page.update_status, fields.status)
                results = other_tasks.run(context, fields, partial_func)
            case 'Return address':
                partial_func = partial(context.edit_page.add_return_shipping_location, fields.return_address)
                results = other_tasks.run(context, fields, partial_func)
            case 'Additional shipping locations':
                addresses = fields.additional_shipping_locations
                partial_func = partial(context.edit_page.add_additional_shipping_locations, addresses)
                results = other_tasks.run(context, fields, partial_func)
            case 'distribution delay':
                partial_func = partial(context.edit_page.update_order_distribution_delay, fields.order_delay)
                results = other_tasks.run(context, fields, partial_func)
            case 'Price restriction':
                partial_func = partial(context.edit_page.update_price_restriction, fields.price_restriction)
                results = other_tasks.run(context, fields, partial_func)
            case 'name field change':
                partial_func = partial(context.edit_page.update_name_section, fields.boutique_name, fields.legal_name)
                results = other_tasks.run(context, fields, partial_func)
            case 'shipping agreement':
                shipping_type = fields.shipping_agreement
                partial_func = partial(context.edit_page.update_shipping_agreement_section, shipping_type)
                results = other_tasks.run(context, fields, partial_func)
            case 'VAT TAX':
                partial_func = partial(context.edit_page.update_vat_number, fields.vat_number)
                results = other_tasks.run(context, fields, partial_func)
            case 'Order email':
                partial_func = partial(context.edit_page.update_order_email, fields.order_email)
                results = other_tasks.run(context, fields, partial_func)
        if not results:
            raise NotImplementedError('the tasks were not handled')
        return process_output(results, task.short_title)

    def run(self, tasks_fields: dict) -> None:
        tasks_to_do = self.podio.prepare_tasks(tasks_fields)
        LoginPage(self.driver, self.user_inputs).login()
        for i, task in enumerate(tasks_to_do[::-1], 1):
            print(f"\n{'':^60}[{i}/{len(tasks_to_do)}] {task.partner_name} {task.task_text}")

            context = Context(self.driver, self.podio, task)
            podio_fields, comments, pdf_files = self.podio.get_partner_details(task.shop_item_id)

            try:
                result = self._manage_tasks(context, task, podio_fields, pdf_files)
            except Exception as e:
                screen = context.add_page.make_screen(f'{podio_fields.boutique_name} -> {e.__class__.__name__}')
                message = handle_exception(screen, e)
                comment = self.podio.add_error_comment(message.err_value, task, comments, self.comment_frequency)
                print(comment)
                continue

            if is_err(result):
                comment = self.podio.add_error_comment(result.err_value, task, comments, self.comment_frequency)
                print(comment)
            elif is_ok(result):
                self.podio.complete_task(task.task_id)
                comment = self.podio.add_comment(result.ok_value, task)
                print(comment)
