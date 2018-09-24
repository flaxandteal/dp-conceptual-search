from enum import Enum
from typing import List

from search.sort_by import SortOrder
from ons.search.fields import AvailableFields, Field


class SortOption(object):
    """
    Simple object to store store options
    """
    def __init__(self, field: Field, sort_order: SortOrder):
        self.field = field
        self.sort_order = sort_order


class SortField(Enum):
    """
    Enum of all available sort options by key
    """
    first_letter: List[SortOption] = [
        SortOption(AvailableFields.TITLE_FIRST_LETTER.value, SortOrder.ASC),
        SortOption(AvailableFields.TITLE_RAW.value, SortOrder.ASC),
        SortOption(AvailableFields.RELEASE_DATE.value, SortOrder.ASC)
    ]
    title: List[SortOption] = [
        SortOption(AvailableFields.TITLE_RAW.value, SortOrder.ASC),
        SortOption(AvailableFields.RELEASE_DATE.value, SortOrder.DESC)
    ]
    relevance: List[SortOption] = [
        SortOption(AvailableFields.SCORE.value, SortOrder.DESC),
        SortOption(AvailableFields.RELEASE_DATE.value, SortOrder.DESC)
    ]
    release_date: List[SortOption] = [
        SortOption(AvailableFields.RELEASE_DATE.value, SortOrder.DESC),
        SortOption(AvailableFields.SCORE.value, SortOrder.DESC)
    ]
    release_date_asc: List[SortOption] = [
        SortOption(AvailableFields.RELEASE_DATE.value, SortOrder.ASC),
        SortOption(AvailableFields.SCORE.value, SortOrder.DESC)
    ]

    @staticmethod
    def available_sort_fields() -> List[str]:
        """
        Returns a list of all available sort fields
        :return:
        """
        return [f.name for f in SortField]

    @staticmethod
    def is_sort_field(label: str) -> bool:
        """
        Returns True is string is a valid SortField, else False
        :param label:
        :return:
        """
        return label in SortField.available_sort_fields()

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
    s = []

    option: SortOption
    for option in sort_field.value:
        d = {
            option.field.name: {
                "order": option.sort_order.value
            }
        }
        s.append(d)

    return s
