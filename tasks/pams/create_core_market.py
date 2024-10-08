import tasks.pams

from apiObjects.podio_api import Podio
from model.podio_item import PartnerFieldsPodio
from pageObjects.pams.create_market_page import CreateMarketPage
from pageObjects.pams.location_info_page import LocationInfoPage
from result import Result, Err, Ok, is_ok, is_err
from tasks.context import Context
from utilites.config_parser import get_config


def _get_list_elem_as_first(origin_list: list, elem_to_move, post_index: int) -> None:
    for elem in origin_list:
        if elem in elem_to_move:
            elem_to_move = origin_list.pop(origin_list.index(elem))
            return origin_list.insert(post_index, elem_to_move)


def sort_core_market_as_first(markets_to_create: list[str], home_market: str) -> list[str]:
    if home_market.upper() in {'DK', 'SE', 'NL', 'BE', 'PL', 'CH', 'NO'} and home_market.upper() in markets_to_create:
        _get_list_elem_as_first(markets_to_create, home_market, 0)
    elif "NL" in markets_to_create:
        _get_list_elem_as_first(markets_to_create, 'NL', 0)
    else:
        markets_succession = {"DK", "BE", "NO", "SE"}
        core_priority = next((market for market in markets_succession if market in markets_to_create), None)
        _get_list_elem_as_first(markets_to_create, core_priority[0], 0)
    return  markets_to_create


def create_core_market(
        create_page_instance: CreateMarketPage, podio_fields: PartnerFieldsPodio, core_market: str
) -> tuple[str, Result]:

    create_page_instance.open_specific_market(core_market)
    create_page_instance.go_to_form_view()
    values_before_update = create_page_instance.get_all_values(create_page_instance.driver.current_url)

    create_page_instance.update_all_fields_in_create_view(core_market, podio_fields)

    save_result = create_page_instance.save()
    if is_err(save_result):
        return core_market, save_result

    changes = create_page_instance.get_differences_between_values(values_before_update)
    return core_market, Ok(changes)


def add_username_and_password_to_podio(podio: Podio, podio_fields: PartnerFieldsPodio, item_id: int) -> tuple[str, str]:
    d = podio_fields.date_of_signing
    v = podio_fields.vat_number
    password = str(d.day).zfill(2) + str(d.month).zfill(2) + 'Success.' + v[-2:]
    podio.update_field(podio_fields.partner_type, item_id, 'username', podio_fields.order_email[0])
    podio.update_field(podio_fields.partner_type, item_id, 'password', password)

    return podio_fields.order_email, password


def create_location(info_page_instance: LocationInfoPage, core_market: str, partner_name: str) -> str:
    pams_location_info_path = get_config('pams_urls_and_paths', 'create_location_path')
    info_page_instance.open(pams_location_info_path)
    info_page_instance.add_location_info(core_market, partner_name)
    info_page_instance.save_location()
    return info_page_instance.get_location_id()


def run(context: Context, podio_fields: PartnerFieldsPodio) -> list[tuple[str, Result[str, str]]]:
    if not podio_fields.username:
        podio_fields.username, podio_fields.password = add_username_and_password_to_podio(
            context.podio, podio_fields, context.task.shop_item_id
        )

    markets = sort_core_market_as_first(podio_fields.markets_to_activate, podio_fields.home_market)
    core_market = markets.pop(0)
    if not podio_fields.pams_partner_id:
        podio_fields.pams_partner_id = create_location(
            context.info_page, core_market, podio_fields.boutique_name
        )
        context.podio.update_field(
            podio_fields.partner_type, context.task.shop_item_id,
            'pams_partner_id', podio_fields.pams_partner_id
        )

    pams_location_info_path = get_config('pams_urls_and_paths', 'location_info_path')
    context.info_page.open(pams_location_info_path.format(location_id=podio_fields.pams_partner_id))
    if core_market not in context.info_page.get_displayed_ids():
        result = create_core_market(context.create_page, podio_fields, core_market)
    else:
        result = core_market, Ok('The market is already created')

    results = []
    if is_ok(result[1]):
        results = tasks.pams.add_new_markets.run(context, podio_fields)

    return [result, *results]
