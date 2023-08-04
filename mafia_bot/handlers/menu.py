
def get_prev_callback(query_data: str) -> str:
    pattern_prefix_length = query_data.find("_") + 1
    pattern_postfix_length = query_data.rfind("_")
    if pattern_prefix_length >= pattern_postfix_length:
        return ''
    return query_data[pattern_prefix_length:pattern_postfix_length]


def get_menu(query_data: str) -> list:
    data = query_data.split("_")
    menu_depth = len(data) // 2
    menu = []
    for i in range(menu_depth):
        menu.append( ( data[i] + "_", data[-(i + 1)] ) )
    return menu


def get_id(query_data: str) -> int | str:
    pattern_prefix_length = query_data.rfind("_") + 1
    id_data = query_data[pattern_prefix_length:]
    try:
        _id = int(id_data)
    except Exception:
        _id = id_data
    return _id
