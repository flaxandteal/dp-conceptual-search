from enum import Enum
from typing import List

from core.search.sort_by import SortOrder
from ons.search.fields import Fields


class SortFields(Enum):
    first_letter = 1,
    title = 2,
    relevance = 3,
    release_date = 4,
    release_date_asc = 5


_sort_by = {
    SortFields.first_letter: [
        (Fields.TITLE_FIRST_LETTER.value, SortOrder.ASC),
        (Fields.TITLE_RAW.value, SortOrder.ASC),
        (Fields.RELEASE_DATE.value, SortOrder.ASC)
    ],
    SortFields.title: [
        (Fields.TITLE_RAW.value, SortOrder.ASC),
        (Fields.RELEASE_DATE.value, SortOrder.DESC)
    ],
    SortFields.relevance: [
        (Fields.SCORE.value, SortOrder.DESC),
        (Fields.RELEASE_DATE.value, SortOrder.DESC)
    ],
    SortFields.release_date: [
        (Fields.RELEASE_DATE.value, SortOrder.DESC),
        (Fields.SCORE.value, SortOrder.DESC)
    ],
    SortFields.release_date_asc: [
        (Fields.RELEASE_DATE.value, SortOrder.ASC),
        (Fields.SCORE.value, SortOrder.DESC)
    ]
}


def query_sort(sort_field: SortFields) -> List[dict]:
    from collections import OrderedDict
    s = []

    for field, order in _sort_by[sort_field]:
        d = OrderedDict()
        d[field.name] = {"order": order.value}
        s.append(d)
    return s