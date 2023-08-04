from collections.abc import Iterable
from typing import Any

from mafia_bot import config

def group_by_pages(
        elements: Iterable[Any],
        pagelen: int = config.BASE_PAGE_LENGTH
) -> Iterable[Iterable[Any]]:
    pages = []
    pagecount = len(elements) // pagelen + int(bool(len(elements) % pagelen))
    for i in range(pagecount):
        pages.append([])
        for j in range(pagelen):
            element_index = i * pagelen + j
            if element_index >= len(elements):
                break
            pages[-1].append(elements[element_index])
    return pages
