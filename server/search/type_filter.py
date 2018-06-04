from server.search.content_types import *


class TypeFilter(object):
    def __init__(self, content_types):
        assert hasattr(
            content_types, "__iter__"), "content_types must be instance of iterable"
        self.content_types = content_types


# Type filters
bulletin_type_filer = TypeFilter([bulletin])
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

filters = {
    "_all": [
        bulletin_type_filer,
        article_type_filter,
        compendia_type_filter,
        time_series_type_filter,
        datasets_type_filter,
        user_requested_data_type_filter,
        qmi_type_filter,
        methodology_type_filter,
        methodology_article_type_filter,
        corporate_information_type_filter
    ],
    bulletin.name: [bulletin_type_filer],
    article.name: [article_type_filter],
    timeseries.name: [time_series_type_filter],
    dataset.name: [datasets_type_filter],
    "user_requested_data": [user_requested_data_type_filter],
    "methodology": [methodology_type_filter],
    "methodology_article": [methodology_article_type_filter],
    "data": [datasets_type_filter, time_series_type_filter, user_requested_data_type_filter],
    "publications": [bulletin_type_filer, compendium_landing_page, article, article_download]
}


def all_filter_funcs():
    content_types_list = []
    for type_filter in filters["_all"]:
        for content_type in type_filter.content_types:
            content_types_list.append(content_type.name)
    return content_types_list
