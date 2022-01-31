def get_section(price: float, low_percentile: float, high_percentile: float):
    section_function = {
        1: price > high_percentile,
        2: low_percentile <= price <= high_percentile,
        3: price < low_percentile
    }

    for section_id in section_function:
        if section_function[section_id]:
            return section_id
    return 3


def get_color_info(section: int):
    return {
        1: ("🔴", " [P] ", "red"),
        2: ("🟠", " [L] ", "orange"),
        3: ("🟢", " [V] ", "green")
    }[section]
