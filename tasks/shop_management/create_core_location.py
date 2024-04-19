from result import Result, is_err, Err, Ok
from tasks.context import Context
from utilites.config_parser import get_config


def _get_list_elem_as_first(origin_list: list, elem_to_move, post_index: int) -> None:
    for elem in origin_list:
        if elem in elem_to_move:
            elem_to_move = origin_list.pop(origin_list.index(elem))
            return origin_list.insert(post_index, elem_to_move)


def _sort_core_market_as_first(all_shop_ids: list[str], home_market: str) -> list[str]:
    prefix_list = {shop_id.split("-")[0] for shop_id in all_shop_ids}

    if home_market.upper() in {'DK', 'SE', 'NL', 'BE', 'PL', 'CH', 'NO'} and home_market.upper() in prefix_list:
        _get_list_elem_as_first(all_shop_ids, home_market, 0)
    elif "NL" in prefix_list:
        _get_list_elem_as_first(all_shop_ids, 'NL', 0)
    else:
        markets_succession = {"DK", "BE", "NO", "SE"}
        core_priority = next((location for location in markets_succession if location in prefix_list), None)
        _get_list_elem_as_first(all_shop_ids, core_priority[0], 0)
    return all_shop_ids


def _convert_shop_ids(podio_data: dict) -> str:
    all_shop_ids = []
    for location in podio_data['locations_to_activate']:
        if f"{location}-" not in podio_data.get('All_Shop_IDs', ''):
            all_shop_ids.append(f'{location}-create')

    if len(all_shop_ids) > 0:
        return ",".join(_sort_core_market_as_first(all_shop_ids, podio_data['Home_Market']))
    return ','.join(all_shop_ids)


def _create_core_market(context: Context, core_market: str) -> list[tuple[str, Result]]:
    if context.podio_data.get('shop_management_id'):
        pams_location_info_path = get_config('shop_management_urls_and_paths', 'location_info_path')
        context.info_page.open(pams_location_info_path.format(location_id=context.podio_data['shop_management_id']))
        context.create_page.location = core_market
        context.create_page.open_specific_market()
    else:
        pams_location_info_path = get_config('urls', 'pams_create_location_path')
        context.info_page.open(pams_location_info_path.format(location_id=context.podio_data['shop_management_id']))
        result = context.info_page.add_location_info_and_go_to_next_step(core_market)
        if is_err(result):
            return [(core_market, result)]

        shop_management_id = context.driver.current_url.split("/")[5]
        context.podio.add_ids([], shop_management_id, context.task)

    create_result = context.create_page.update_all_fields_in_create_view()
    if is_err(create_result):
        return [(core_market, create_result)]

    final_result = context.create_page.save_create_view({})
    return [(core_market, final_result)]


def run(context: Context) -> Result:
    origin_shop_ids = _convert_shop_ids(context.podio_data).split(',')
    core_market = origin_shop_ids[0].split('-')[0]

    create_result = _create_core_market(context, core_market)
    converted_output = context.create_page.process_output(create_result)
    if is_err(converted_output):
        return converted_output

    result = context.info_page.wait_for_ids([core_market])
    all_shop_ids = _sort_core_market_as_first(result.value[1], context.podio_data['Home_Market'])
    context.podio.add_ids(all_shop_ids, context.podio_data['shop_management_id'], context.task)

    if is_err(result):
        return Err(f'\n\n{result.err_value[0]}')
    return converted_output
