"""
Content types lifted out of Babbage
"""
from enum import Enum
from typing import List


class ContentTypeWeights(Enum):
    """
    Enum containing content type weight constants
    """
    DEFAULT = 1.0
    BULLETIN = 1.55
    ARTICLE = 1.30
    TIMESERIES = 1.20
    STATIC_ADHOC = 1.25
    DATASET_LANDING_PAGE = 1.35


class ContentType(object):
    def __init__(self, name, weight: ContentTypeWeights=ContentTypeWeights.DEFAULT):
        self.name = name
        self.weight = weight

    def __str__(self):
        return "ContentType: {0}(weight={1})".format(self.name, self.weight.value)

    def __repr__(self):
        return "ContentType: {0}(weight={1})".format(self.name, self.weight.value)

    def filter_function(self) -> dict:
        """
        Generates a filter function query block for the given content type
        :return:
        """
        return {
            "filter": {
                "term": {
                    "_type": self.name
                }
            },
            "weight": self.weight.value
        }


class ContentTypes(Enum):
    """
    Enum containing all available content types
    """
    HOME_PAGE = ContentType("home_page")
    HOME_PAGE_CENSUS = ContentType("home_page_census")
    TAXONOMY_LANDING_PAGE = ContentType("taxonomy_landing_page")
    PRODUCT_PAGE = ContentType("product_page")
    BULLETIN = ContentType("bulletin", ContentTypeWeights.BULLETIN)
    ARTICLE = ContentType("article", ContentTypeWeights.ARTICLE)
    ARTICLE_DOWNLOAD = ContentType("article_download", ContentTypeWeights.ARTICLE)
    TIMESERIES = ContentType("timeseries", ContentTypeWeights.TIMESERIES)
    DATA_SLICE = ContentType("data_slice")
    COMPENDIUM_LANDING_PAGE = ContentType("compendium_landing_page", ContentTypeWeights.ARTICLE)
    COMPENDIUM_CHAPTER = ContentType("compendium_chapter")
    COMPENDIUM_DATA = ContentType("compendium_data")
    STATIC_LANDING_PAGE = ContentType("static_landing_page")
    STATIC_ARTICLE = ContentType("static_article")
    STATIC_METHODOLOGY = ContentType("static_methodology")
    STATIC_METHODOLOGY_DOWNLOAD = ContentType("static_methodology_download")
    STATIC_PAGE = ContentType("static_page")
    STATIC_QMI = ContentType("static_qmi", ContentTypeWeights.BULLETIN)
    STATIC_FOI = ContentType("static_foi")
    STATIC_ADHOC = ContentType("static_adhoc", ContentTypeWeights.STATIC_ADHOC)
    DATASET = ContentType("dataset")
    DATASET_LANDING_PAGE = ContentType("dataset_landing_page", ContentTypeWeights.DATASET_LANDING_PAGE)
    TIMESERIES_DATASET = ContentType("timeseries_dataset")
    RELEASE = ContentType("release")
    REFERENCE_TABLES = ContentType("reference_tables")
    CHART = ContentType("chart")
    TABLE = ContentType("table")
    EQUATION = ContentType("equation")
    DEPARTMENTS = ContentType("departments")


def get_all_content_types() -> List[ContentType]:
    """
    Returns a list of all available content types
    :return:
    """
    return [content_type.value for content_type in ContentTypes]
