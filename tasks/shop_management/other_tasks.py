from result import Result, is_err
from tasks.context import Context
from utilites.config_parser import get_config


def process_changes(context: Context, method: callable) -> Result[str, str]:
    pams_location_info_path = get_config('shop_management_urls_and_paths', 'location_info_path')
    context.info_page.open(pams_location_info_path.format(location_id=context.podio_data['shop_management_id']))

    results = []
    for shop_id in context.podio_data['All_Shop_IDs'].split(','):
        context.edit_page.location = shop_id.split('-')[0]
        context.edit_page.open_specific_market()

        values_before_update = context.edit_page.get_all_values(context.driver.current_url)
        update_results = method()
        if is_err(update_results):
            return update_results
        save_results = context.edit_page.save(values_before_update)

        results.append((context.edit_page.location, save_results))

    return context.edit_page.process_output(results)


def run(context: Context, method: callable) -> Result[str, str]:
    return process_changes(context, method)
