from enum import Enum
from typing import List

from core.search.sort_by import SortOrder
from ons.search.fields import Fields


class SortOption(object):
    """
    Simple object to store store options
    """
    def __init__(self, field: Fields, sort_order: SortOrder):
        self.field = field
        self.sort_order = sort_order


class SortField(Enum):
    """
    Enum of all available sort options by key
    """
    first_letter: List[SortOption] = [
        SortOption(Fields.TITLE_FIRST_LETTER, SortOrder.ASC),
        SortOption(Fields.TITLE_RAW, SortOrder.ASC),
        SortOption(Fields.RELEASE_DATE, SortOrder.ASC)
    ]
    title: List[SortOption] = [
        SortOption(Fields.TITLE_RAW, SortOrder.ASC),
        SortOption(Fields.RELEASE_DATE, SortOrder.DESC)
    ]
    relevance: List[SortOption] = [
        SortOption(Fields.SCORE, SortOrder.DESC),
        SortOption(Fields.RELEASE_DATE, SortOrder.DESC)
    ]
    release_date: List[SortOption] = [
        SortOption(Fields.RELEASE_DATE, SortOrder.DESC),
        SortOption(Fields.SCORE, SortOrder.DESC)
    ]
    release_date_asc: List[SortOption] = [
        SortOption(Fields.RELEASE_DATE, SortOrder.ASC),
        SortOption(Fields.SCORE, SortOrder.DESC)
    ]

    @staticmethod
    def available_sort_fields():
        """
        Returns a list of all available sort fields
        :return:
        """
        return [f.name for f in SortField]

    @staticmethod
    def is_sort_field(label: str):
        """
        Returns True is string is a valid SortField, else False
        :param label:
        :return:
        """
        return label in SortField.available_sort_fields

    @staticmethod
    def from_str(label: str) -> 'SortField':
        """
        Returns the enum type corresponding to the input string
        :param label:
        :return:
        """

        if SortField.is_sort_field(label):
            return SortField[label]
        else:
            raise NotImplementedError("No such SortField for string: '{0}'".format(label))


def query_sort(sort_field: SortField) -> List[dict]:
    from collections import OrderedDict
    s = []

    option: SortOption
    for option in sort_field.value:
        d = OrderedDict()
        d[option.field.value] = {"order": option.sort_order.value}
        s.append(d)
    return s
