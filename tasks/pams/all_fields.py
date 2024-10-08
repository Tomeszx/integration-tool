from result import Result, Err, Ok, is_err
from model.podio_item import PartnerFieldsPodio
from pageObjects.pams.edit_market_page import EditMarketPage
from tasks.context import Context
from utilites.config_parser import get_config


def process_changes(
        edit_page_instance: EditMarketPage, fields: PartnerFieldsPodio, markets: dict.keys
) -> list[tuple[str, Result]]:
    results = []
    for market in markets:
        edit_page_instance.open_specific_market(market)
        edit_page_instance.go_to_form_view()
        values_before_update = edit_page_instance.get_all_values(edit_page_instance.driver.current_url)

        edit_page_instance.update_all_fields_in_edit_view(market, fields)

        save_result = edit_page_instance.save()
        if is_err(save_result):
            results.append((market, save_result))
            return results
        else:
            changes = edit_page_instance.get_differences_between_values(values_before_update)
            results.append((market, Ok(changes)))

    return results


def run(context: Context, podio_fields: PartnerFieldsPodio) -> list[tuple[str, Result[str, str]]]:
    pams_location_preview_path = get_config('pams_urls_and_paths', 'location_info_path')
    url = pams_location_preview_path.format(location_id=podio_fields.pams_partner_id)
    context.info_page.open(url)

    available_ids = context.info_page.get_displayed_ids()
    results = process_changes(context.edit_page, podio_fields, available_ids.keys())

    return results
