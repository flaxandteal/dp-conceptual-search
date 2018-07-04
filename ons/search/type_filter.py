from ons.search.content_type import *

from typing import List


class TypeFilter(object):
    def __init__(self, content_types_list: List[ContentType]):
        self.content_types = content_types_list


# Type filters
bulletin_type_filter = TypeFilter([bulletin])
article_type_filter = TypeFilter([article, article_download])
compendia_type_filter = TypeFilter([compendium_landing_page])
time_series_type_filter = TypeFilter([timeseries])
datasets_type_filter = TypeFilter([dataset_landing_page, reference_tables])
user_requested_data_type_filter = TypeFilter([static_adhoc])
qmi_type_filter = TypeFilter([static_qmi])
methodology_type_filter = TypeFilter(
    [static_qmi, static_methodology, static_methodology_download])
methodology_article_type_filter = TypeFilter(
    [static_methodology, static_methodology_download])
corporate_information_type_filter = TypeFilter(
    [static_foi, static_page, static_landing_page, static_article])


_default_filters = [
        bulletin_type_filter,
        article_type_filter,
        compendia_type_filter,
        time_series_type_filter,
        datasets_type_filter,
        user_requested_data_type_filter,
        qmi_type_filter,
        methodology_type_filter,
        methodology_article_type_filter,
        corporate_information_type_filter]


"""
Mapping of filter name to content types - should be dict[str, list]
"""
_filters = {
    "_all": _default_filters,
    bulletin.name: [bulletin_type_filter],
    article.name: [article_type_filter],
    timeseries.name: [time_series_type_filter],
    dataset.name: [datasets_type_filter],
    "compendium_landing_page": [compendia_type_filter],
    static_adhoc.name: [user_requested_data_type_filter],
    "methodology": [methodology_type_filter],
    "methodology_article": [methodology_article_type_filter],
    "ons": _default_filters,
    "onsdata": [
        datasets_type_filter,
        time_series_type_filter,
        user_requested_data_type_filter],
    "onspublications": [
        bulletin_type_filter,
        compendia_type_filter,
        article_type_filter]}


def default_filters():
    return filters_for_type("_all")


def available_filters():
    return _filters.keys()


def filters_for_type(filter_type):
    filters = []
    if isinstance(filter_type, str):
        filter_type = [filter_type]

    for ftype in filter_type:
        if ftype in _filters:
            for type_filter in _filters.get(ftype):
                for content_type in type_filter.content_types:
                    filters.append(content_type.name)
    return filters
