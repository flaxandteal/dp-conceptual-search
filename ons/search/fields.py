from enum import Enum
from typing import List


class Field(object):
    def __init__(self, name, boost=None, highlight=False):
        self.name = name
        self.boost = boost
        self.highlight = highlight

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @property
    def field_name_boosted(self):
        return "%s^%d" % (self.name, int(self.boost)
                          ) if self.boost is not None else self.name


class Fields(Enum):
    URI = Field("uri")
    SCORE = Field("_score")
    TITLE_NO_DATES = Field("description.title.title_no_dates", 10)
    TITLE_FIRST_LETTER = Field("description.title.title_first_letter")
    TITLE_RAW = Field("description.title.title_raw")
    TITLE = Field("description.title", 10, highlight=True)
    TITLE_NO_STEM = Field("description.title.title_no_stem", 10)
    TITLE_NO_SYNONYM_NO_STEM = Field("description.title.title_no_synonym_no_stem")  # used for suggestions
    EDITION = Field("description.edition", highlight=True)
    SUMMARY = Field("description.summary", highlight=True)
    RELEASE_DATE = Field("description.releaseDate")
    LAST_REVISED = Field("description.lastRevised")
    META_DESCRIPTION = Field("description.metaDescription", highlight=True)
    KEYWORDS = Field("description.keywords", highlight=True)
    KEYWORDS_RAW = Field("description.keywords.keywords_raw", highlight=True)
    TYPE = Field("_type")
    CDID = Field("description.cdid", highlight=True)
    DATASET_ID = Field("description.datasetId", highlight=True)
    SEARCH_BOOST = Field("searchBoost", 100)
    LATEST_RELEASE = Field("description.latestRelease")
    PUBLISHED = Field("description.published")
    CANCELLED = Field("description.cancelled")
    TOPICS = Field("topics")
    EMBEDDING_VECTOR = Field("embedding_vector")


def get_all_fields() -> List[Field]:
    """
    Returns a list of all available fields
    :return:
    """
    fields = [field.value for field in list(Fields)]
    return fields
