from enum import Enum
from typing import List

from dp_conceptual_search.ons.search.content_type import ContentType, AvailableContentTypes


class TypeFilter(object):
    """
    Specifies a list of content types for this type filter
    """
    def __init__(self, content_type_filters: List[ContentType]):
        self._content_type_filters = content_type_filters

    def get_content_types(self) -> List[ContentType]:
        return self._content_type_filters


class AvailableTypeFilters(Enum):
    """
    Enum of available type filters for the ONS website
    """
    BULLETIN = TypeFilter([AvailableContentTypes.BULLETIN.value])
    ARTICLE = TypeFilter([AvailableContentTypes.ARTICLE.value, AvailableContentTypes.ARTICLE_DOWNLOAD.value])
    COMPENDIA = TypeFilter([AvailableContentTypes.COMPENDIUM_LANDING_PAGE.value])
    TIME_SERIES = TypeFilter([AvailableContentTypes.TIMESERIES.value])
    DATASETS = TypeFilter([AvailableContentTypes.DATASET_LANDING_PAGE.value, AvailableContentTypes.REFERENCE_TABLES.value])
    USER_REQUESTED_DATA = TypeFilter([AvailableContentTypes.STATIC_ADHOC.value])
    QMI = TypeFilter([AvailableContentTypes.STATIC_QMI.value])
    METHODOLOGY = TypeFilter([AvailableContentTypes.STATIC_QMI.value, AvailableContentTypes.STATIC_METHODOLOGY.value,
                              AvailableContentTypes.STATIC_METHODOLOGY_DOWNLOAD.value])
    METHODOLOGY_ARTICLE = TypeFilter([AvailableContentTypes.STATIC_METHODOLOGY.value, AvailableContentTypes.STATIC_METHODOLOGY_DOWNLOAD.value])
    CORPORATE_INFO = TypeFilter([AvailableContentTypes.STATIC_FOI.value, AvailableContentTypes.STATIC_PAGE.value, AvailableContentTypes.STATIC_LANDING_PAGE.value,
                                 AvailableContentTypes.STATIC_ARTICLE.value])
    # Type filter for featured results queries
    FEATURED = TypeFilter([AvailableContentTypes.PRODUCT_PAGE.value, AvailableContentTypes.HOME_PAGE_CENSUS.value])
