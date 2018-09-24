from typing import List
from enum import Enum

from ons.search.content_type import ContentTypes
from ons.search.exceptions.unknown_type_filter_exception import UnknownTypeFilter


class TypeFilter(object):
    """
    Specifies a list of content types for this type filter
    """
    def __init__(self, content_type_filters: List[ContentTypes]):
        self.content_type_filters = content_type_filters

    def get_content_types(self) -> List[ContentTypes]:
        return [content_type.value for content_type in self.content_type_filters]


class TypeFilters(Enum):
    """
    Enum of available type filters for the ONS website
    """
    BULLETIN = TypeFilter([ContentTypes.BULLETIN])
    ARTICLE = TypeFilter([ContentTypes.ARTICLE, ContentTypes.ARTICLE_DOWNLOAD])
    COMPENDIA = TypeFilter([ContentTypes.COMPENDIUM_LANDING_PAGE])
    TIME_SERIES = TypeFilter([ContentTypes.TIMESERIES])
    DATASETS = TypeFilter([ContentTypes.DATASET_LANDING_PAGE, ContentTypes.REFERENCE_TABLES])
    USER_REQUESTED_DATA = TypeFilter([ContentTypes.STATIC_ADHOC])
    QMI = TypeFilter([ContentTypes.STATIC_QMI])
    METHODOLOGY = TypeFilter([ContentTypes.STATIC_QMI, ContentTypes.STATIC_METHODOLOGY,
                              ContentTypes.STATIC_METHODOLOGY_DOWNLOAD])
    METHODOLOGY_ARTICLE = TypeFilter([ContentTypes.STATIC_METHODOLOGY, ContentTypes.STATIC_METHODOLOGY_DOWNLOAD])
    CORPORATE_INFO = TypeFilter([ContentTypes.STATIC_FOI, ContentTypes.STATIC_PAGE, ContentTypes.STATIC_LANDING_PAGE,
                                 ContentTypes.STATIC_ARTICLE])
    # Type filter for featured results queries
    FEATURED = TypeFilter([ContentTypes.PRODUCT_PAGE, ContentTypes.HOME_PAGE_CENSUS])

    @staticmethod
    def all() -> List['TypeFilter']:
        """
        Returns all available TypeFilters
        :return:
        """
        return [e.value for e in list(TypeFilters)]

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
            if TypeFilters.is_type_filter(type_filter_str):
                type_filters.append(TypeFilters.from_str(type_filter_str).value)
            else:
                # Check if known content type and if True, add type filter
                if ContentTypes.is_content_type(type_filter_str):
                    type_filters.append(TypeFilter([ContentTypes.from_str(type_filter_str)]))
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
        return [f.name for f in TypeFilters]

    @staticmethod
    def is_type_filter(label: str) -> bool:
        """
        Returns True is string is a valid TypeFilter, else False. Makes case insensitive comparison.
        :param label:
        :return:
        """
        return label.upper() in TypeFilters.available_type_filters()

    @staticmethod
    def from_str(label: str) -> 'TypeFilters':
        """
        Returns the enum type corresponding to the input string
        :param label:
        :return:
        """

        if TypeFilters.is_type_filter(label):
            return TypeFilters[label.upper()]
        else:
            raise NotImplementedError("No such TypeFilter for string: '{0}'".format(label))
