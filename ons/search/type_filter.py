from typing import List
from enum import Enum
from ons.search.content_type import *


class TypeFilter(object):
    """
    Specifies a list of content types for this type filter
    """
    def __init__(self, content_type_filters: List[ContentType]):
        self.content_type_filters = content_type_filters

    def get_content_types(self) -> List[ContentType]:
        return self.content_type_filters


class TypeFilters(Enum):
    """
    Enum of available type filters for the ONS website
    """
    BULLETIN = TypeFilter([bulletin])
    ARTICLE = TypeFilter([article, article_download])
    COMPENDIA = TypeFilter([compendium_landing_page])
    TIME_SERIES = TypeFilter([timeseries])
    DATASETS = TypeFilter([dataset_landing_page, reference_tables])
    USER_REQUESTED_DATA = TypeFilter([static_adhoc])
    QMI = TypeFilter([static_qmi])
    METHODOLOGY = TypeFilter([static_qmi, static_methodology, static_methodology_download])
    METHODOLOGY_ARTICLE = TypeFilter([static_methodology, static_methodology_download])
    CORPORATE_INFO = TypeFilter([static_foi, static_page, static_landing_page, static_article])
