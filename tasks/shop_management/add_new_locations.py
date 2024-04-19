from result import Result, is_err, Err
from tasks.context import Context
from utilites.config_parser import get_config


def _convert_shop_ids(podio_data: dict) -> str:
    all_shop_ids = []
    for location in podio_data['Markets_to_activate_for_the_partner']:
        if f"{location}-" not in podio_data['All_Shop_IDs']:
            all_shop_ids.append(f'{location}-create')
    return ','.join(all_shop_ids)


def _process_changes(context: Context, shop_ids: list) -> Result[str, str]:
    pams_location_info_path = get_config('shop_management_urls_and_paths', 'location_info_path')
    context.info_page.open(pams_location_info_path.format(location_id=context.podio_data['shop_management_id']))

    results = []
    for shop_id in shop_ids:
        context.add_page.location = shop_id.split('-')[0]
        context.add_page.open_specific_market()

        values_before_update = context.add_page.get_all_values(context.driver.current_url)
        update_results = context.add_page.update_all_fields_in_add_view()
        if is_err(update_results):
            return update_results
        save_results = context.add_page.save(values_before_update)

        results.append((context.add_page.location, save_results))

    return context.edit_page.process_output(results)


def run(context: Context) -> Result[str, str]:
    shop_ids = _convert_shop_ids(context.podio_data).split(',')
    context.info_page.open(f"/preview/{context.podio_data['shop_management_id']}/info")

    create_results = _process_changes(context, shop_ids)

    waiting_result = context.info_page.wait_for_ids(shop_ids)
    all_shop_ids = context.podio_data['All_Shop_IDs'].split(',') + waiting_result.value[1]
    context.podio.add_ids(all_shop_ids, context.podio_data['shop_management_id'], context.task)

    if is_err(waiting_result):
        return Err(waiting_result.err_value[0] + f'\n{create_results.value}')
    return create_results



