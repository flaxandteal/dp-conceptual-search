from typing import List
from enum import Enum
from ons.search.content_type import ContentTypes, ContentType


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
