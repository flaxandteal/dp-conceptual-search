"""
Enum of all available ONS list_types and default type filters associated with them
"""
from enum import Enum
from typing import List, Iterable

from dp_conceptual_search.ons.search.type_filter import AvailableTypeFilters, TypeFilter


class ListType(Enum):
    # Default list_type - default to all available type filters
    ONS: List[AvailableTypeFilters] = list(AvailableTypeFilters)

    # Returns datasets only
    ONSDATA: List[AvailableTypeFilters] = [
        AvailableTypeFilters.DATASETS,
        AvailableTypeFilters.TIME_SERIES,
        AvailableTypeFilters.USER_REQUESTED_DATA
    ]

    # Returns publications only
    ONSPUBLICATIONS: List[AvailableTypeFilters] = [
        AvailableTypeFilters.BULLETIN,
        AvailableTypeFilters.COMPENDIA,
        AvailableTypeFilters.ARTICLE
    ]

    @property
    def value(self) -> Iterable['AvailableTypeFilters']:
        """
        Implements 'value' from super with additional type information
        :return:
        """
        return super(ListType, self).value

    @staticmethod
    def available_list_types() -> List[str]:
        """
        Returns a list of all available list types
        :return:
        """
        return [f.name for f in ListType]

    @staticmethod
    def is_list_type(label: str) -> bool:
        """
        Returns True is string is a valid ListType, else False. Makes case insensitive comparison.
        :param label:
        :return:
        """
        return label.upper() in ListType.available_list_types()

    @staticmethod
    def from_str(label: str) -> 'ListType':
        """
        Returns the enum type corresponding to the input string
        :param label:
        :return:
        """

        if ListType.is_list_type(label):
            return ListType[label.upper()]
        else:
            raise NotImplementedError("No such ListType for string: '{0}'".format(label))

    def to_type_filters(self) -> List[TypeFilter]:
        """
        Helper function for converting from a list of AvailableTypeFilters to a list of TypeFilter
        :return:
        """
        type_filters: List[TypeFilter] = []

        type_filter: AvailableTypeFilters
        for type_filter in self.value:
            type_filters.append(type_filter.value)

        return type_filters
