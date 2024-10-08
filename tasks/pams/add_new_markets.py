from result import Result, Err, Ok, is_ok, is_err
from apiObjects.google_sheet_api import upload_file
from model.podio_item import PartnerFieldsPodio
from pageObjects.pams.add_new_market_page import AddMarketPage
from tasks.context import Context
from utilites.config_parser import get_config


def add_new_market(add_page_instance: AddMarketPage, podio_fields: PartnerFieldsPodio, market: str) -> Result[str, str]:
    add_page_instance.open_specific_market(market)
    add_page_instance.go_to_form_view()
    values_before_update = add_page_instance.get_all_values(add_page_instance.driver.current_url)
    add_page_instance.update_all_fields_in_add_view(market, podio_fields)
    save_result = add_page_instance.save()
    if is_err(save_result):
        return save_result

    changes = add_page_instance.get_differences_between_values(values_before_update)
    return Ok(changes)


def process_changes(
        add_page_instance: AddMarketPage, podio_fields: PartnerFieldsPodio, created_markets: dict.keys
) -> list[tuple[str, Result]]:
    results = []
    for shop_id in podio_fields.markets_to_activate:
        if shop_id.split('-')[0] in created_markets:
            continue

        market = shop_id.split('-')[0]
        result = add_new_market(add_page_instance, podio_fields, market)
        results.append((market, result))

    return results


def send_ids_to_podio(context: Context, partner_type: str, created_ids: dict[str, str]) -> None:
    all_ids_text = ",".join(f'{market.upper()}-{shop_id}' for market, shop_id in created_ids.items())
    context.podio.update_field(partner_type, context.task.shop_item_id, 'all_shop_ids', all_ids_text)


def run(context: Context, podio_fields: PartnerFieldsPodio) -> list[tuple[str, Result[str, str]]]:
    pams_location_preview_path = get_config('pams_urls_and_paths', 'location_info_path')
    url = pams_location_preview_path.format(location_id=podio_fields.pams_partner_id)
    context.info_page.open(url)

    already_created_ids = context.info_page.get_displayed_ids()
    if len(already_created_ids) >= len(podio_fields.markets_to_activate):
        send_ids_to_podio(context, podio_fields.partner_type, already_created_ids)
        return [('all_markets', Ok('All markets are already created in PaMS.'))]

    loading_markets = context.info_page.check_if_any_market_is_loading()
    assert is_ok(loading_markets), loading_markets.err_value

    create_results = process_changes(context.add_page, podio_fields, already_created_ids.keys())
    created_ids = context.info_page.wait_for_ids(podio_fields.pams_partner_id)
    if len(created_ids) < len(podio_fields.markets_to_activate):
        screen_url = upload_file(context.info_page.make_screen(' waiting for ids'))
        error_comment = f"Couldn't map all created ids in PaMS.\nScreenshot: {screen_url}"
        return [('', Err(error_comment)), *create_results]

    send_ids_to_podio(context, podio_fields.partner_type, created_ids)

    return create_results
