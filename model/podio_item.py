import json

from bs4 import BeautifulSoup
from datetime import datetime, date

from phonenumbers import format_number, PhoneNumberFormat, parse
from result import Err, Result, Ok

from model.address import ReturnAddress, ShippingAddresses
from utilites.config_parser import get_podio_fields_ids


def extract_text_field(field: dict | None) -> str | None:
    if not field:
        return None
    html_text = BeautifulSoup(field['values'][0]['value'], 'html.parser')
    return html_text.get_text().replace("\xa0", " ")


def extract_phone_field(field: dict | None, home_market: str) -> str | None:
    if not field:
        return None

    phone_number = extract_text_field(field)
    try:
        return format_number(parse(phone_number), PhoneNumberFormat.E164)
    except Exception:
        try:
            return format_number(parse(phone_number, home_market), PhoneNumberFormat.E164)
        except Exception as e:
            print(f'{e=}\n{home_market=}')
            return None


def extract_date_field(field: dict | None) -> date | None:
    if not field:
        return None
    return datetime.strptime(field['values'][0]['start_date'], "%Y-%m-%d").date()


def extract_category_field(field: dict | None) -> str | None:
    if not field:
        return None
    return field['values'][0]['value']['text']


def extract_multiple_category_field(field: dict | None) -> list[str] | None:
    if not field:
        return None
    return [details['value']['text'] for details in field['values']]


def extract_email_field(field: dict | None) -> list[str] | None:
    if not field:
        return None
    return [details['value'] for details in field['values']]



def extract_contact_field(field: dict | None) -> list[str] | None:
    if not field:
        return None
    return [value['value']['name'] for value in field['values'] if isinstance(value, dict)]


class PartnerFieldsPodio:
    def __init__(self, original_fields: list[dict], partner_type: str):
        ids_map = get_podio_fields_ids(partner_type)
        fields = {field['field_id']: field for field in original_fields}

        self.partner_type = partner_type
        self.boutique_name = extract_text_field(fields.get(ids_map['boutique_name']))
        self.legal_name = extract_text_field(fields.get(ids_map['legal_name']))
        self.pc_location_name = extract_text_field(fields.get(ids_map['pc_location_name']))
        self.all_shop_ids = extract_text_field(fields.get(ids_map['all_shop_ids']))
        self.primary_shop_id = extract_text_field(fields.get(ids_map['primary_shop_id']))
        self.date_of_signing = extract_date_field(fields.get(ids_map['date_of_signing']))
        self.status = extract_category_field(fields.get(ids_map['status']))
        self.home_market = extract_category_field(fields.get(ids_map['home_market']))
        self.markets_to_activate = extract_multiple_category_field(fields.get(ids_map['markets_to_activate']))
        self.order_email = extract_email_field(fields.get(ids_map['order_email']))
        self.username = extract_text_field(fields.get(ids_map['username']))
        self.password = extract_text_field(fields.get(ids_map['password']))
        self.shipping_agreement = extract_category_field(fields.get(ids_map['shipping_agreement']))
        self.shipping_street = extract_text_field(fields.get(ids_map['shipping_street']))
        self.shipping_zip_code = extract_text_field(fields.get(ids_map['shipping_zip_code']))
        self.shipping_city = extract_text_field(fields.get(ids_map['shipping_city']))
        self.shipping_country = extract_category_field(fields.get(ids_map['shipping_country']))
        self.vat_number = extract_text_field(fields.get(ids_map['vat_number']))
        self.iban = extract_text_field(fields.get(ids_map['iban']))
        self.bank_code = extract_text_field(fields.get(ids_map['bank_code']))
        self.invoicing_street = extract_text_field(fields.get(ids_map['invoicing_street']))
        self.invoicing_zip_code = extract_text_field(fields.get(ids_map['invoicing_zip_code']))
        self.invoicing_city = extract_text_field(fields.get(ids_map['invoicing_city']))
        self.invoicing_country = extract_category_field(fields.get(ids_map['invoicing_country']))
        self.invoicing_email = extract_email_field(fields.get(ids_map['invoicing_email']))
        self.pams_partner_id = extract_text_field(fields.get(ids_map['pams_partner_id']))
        self.price_restriction = int(float(extract_text_field(fields.get(ids_map['price_restriction'])) or 0))
        self.order_delay = int(float(extract_text_field(fields.get(ids_map['order_delay'])) or 0))
        self.contact_person = extract_text_field(fields.get(ids_map['contact_person']))
        self.onboard_responsible = extract_contact_field(fields.get(ids_map['onboard_responsible']))
        self.signed_by = extract_contact_field(fields.get(ids_map['signed_by']))
        self.contact_email = extract_email_field(fields.get(ids_map['contact_email']))
        self.contact_phone = extract_phone_field(fields.get(ids_map['contact_phone']), self.home_market)

        self.pure_commission = extract_text_field(fields.get(ids_map['pure_commission']))
        if self.pure_commission:
            self.pure_commission = int(float(self.pure_commission))
        self.additional_shipping_locations = extract_text_field(fields.get(ids_map['additional_shipping_locations']))
        if self.additional_shipping_locations:
            self.additional_shipping_locations = ShippingAddresses.from_string(self.additional_shipping_locations)
        self.return_address = extract_text_field(fields.get(ids_map['return_address']))
        if self.return_address:
            self.return_address = ReturnAddress.from_string(self.return_address)



    def __getitem__(self, item: str) -> str | int | None:
        return self.__dict__[item]

    def check_required_fields(self, required_tasks: dict) -> Result[None, str]:
        for field in required_tasks:
            if not self[field]:
                return Err(f'The {field} field is empty or incorrect in Podio. Please fix this field.')
        return Ok(None)


class PdfFile:
    def __init__(self, files: list[dict]):
        self.has_pdf = False
        for files in files:
            if files["name"].lower().endswith('.pdf'):
                self.has_pdf = True
                return

    def __bool__(self) -> bool:
        return self.has_pdf


class Comment:
    def __init__(self, comment: dict):
        self.created_on = comment['created_on']
        self.value = comment['value']


class Comments:
    def __init__(self, comments: list[dict]):
        self.data = [Comment(comment) for comment in comments if comment['created_by']["name"] == "Update Admins"]

