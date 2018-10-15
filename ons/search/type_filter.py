from enum import Enum
from typing import List, Iterable

from ons.search.content_type import AvailableContentTypes
from ons.search.exceptions.unknown_type_filter_exception import UnknownTypeFilter


class TypeFilter(object):
    """
    Specifies a list of content types for this type filter
    """
    def __init__(self, content_type_filters: List[AvailableContentTypes]):
        self.content_type_filters = content_type_filters

    def get_content_types(self) -> List[AvailableContentTypes]:
        return self.content_type_filters


class AvailableTypeFilters(Enum):
    """
    Enum of available type filters for the ONS website
    """
    BULLETIN = TypeFilter([AvailableContentTypes.BULLETIN])
    ARTICLE = TypeFilter([AvailableContentTypes.ARTICLE, AvailableContentTypes.ARTICLE_DOWNLOAD])
    COMPENDIA = TypeFilter([AvailableContentTypes.COMPENDIUM_LANDING_PAGE])
    TIME_SERIES = TypeFilter([AvailableContentTypes.TIMESERIES])
    DATASETS = TypeFilter([AvailableContentTypes.DATASET_LANDING_PAGE, AvailableContentTypes.REFERENCE_TABLES])
    USER_REQUESTED_DATA = TypeFilter([AvailableContentTypes.STATIC_ADHOC])
    QMI = TypeFilter([AvailableContentTypes.STATIC_QMI])
    METHODOLOGY = TypeFilter([AvailableContentTypes.STATIC_QMI, AvailableContentTypes.STATIC_METHODOLOGY,
                              AvailableContentTypes.STATIC_METHODOLOGY_DOWNLOAD])
    METHODOLOGY_ARTICLE = TypeFilter([AvailableContentTypes.STATIC_METHODOLOGY, AvailableContentTypes.STATIC_METHODOLOGY_DOWNLOAD])
    CORPORATE_INFO = TypeFilter([AvailableContentTypes.STATIC_FOI, AvailableContentTypes.STATIC_PAGE, AvailableContentTypes.STATIC_LANDING_PAGE,
                                 AvailableContentTypes.STATIC_ARTICLE])
    # Type filter for featured results queries
    FEATURED = TypeFilter([AvailableContentTypes.PRODUCT_PAGE, AvailableContentTypes.HOME_PAGE_CENSUS])

    @staticmethod
    def all() -> List['TypeFilter']:
        """
        Returns all available TypeFilters
        :return:
        """
        return [e.value for e in list(AvailableTypeFilters)]

    @property
    def value(self) -> TypeFilter:
        """
        Implements 'value' from super with additional type information
        :return:
        """
        return super(AvailableTypeFilters, self).value

    @staticmethod
    def from_string_list(type_filter_strings: List[str]) -> List['TypeFilter']:
        """
        Parses a list of string type filters and returns enum types.
        If there is no known TypeFilter but a known ContentType, then returns a custom type filter
        :param type_filter_strings:
        :return:
        """
        type_filters: List[TypeFilter] = []

        for type_filter_str in type_filter_strings:
            if AvailableTypeFilters.is_type_filter(type_filter_str):
                type_filters.append(AvailableTypeFilters.from_str(type_filter_str).value)
            else:
                # Check if known content type and if True, add type filter
                if AvailableContentTypes.is_content_type(type_filter_str):
                    type_filters.append(TypeFilter([AvailableContentTypes.from_str(type_filter_str)]))
                else:
                    # Raise an exception (we don't know how to deal with this type filter/content type
                    raise UnknownTypeFilter(type_filter_str)

        return type_filters

    @staticmethod
    def available_type_filters() -> List[str]:
        """
        Returns a list of all available type filters
        :return:
        """
        return [f.name for f in AvailableTypeFilters]

    @staticmethod
    def is_type_filter(label: str) -> bool:
        """
        Returns True is string is a valid TypeFilter, else False. Makes case insensitive comparison.
        :param label:
        :return:
        """
        return label.upper() in AvailableTypeFilters.available_type_filters()

    @staticmethod
    def from_str(label: str) -> 'AvailableTypeFilters':
        """
        Returns the enum type corresponding to the input string
        :param label:
        :return:
        """

        if AvailableTypeFilters.is_type_filter(label):
            return AvailableTypeFilters[label.upper()]
        else:
            raise NotImplementedError("No such TypeFilter for string: '{0}'".format(label))
