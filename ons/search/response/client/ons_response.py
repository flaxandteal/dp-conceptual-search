import logging
from typing import List

from elasticsearch_dsl.response import Response
from elasticsearch_dsl.response import Hit, HitMeta

from ons.search.sort_fields import SortField
from ons.search.response import SearchResult, ContentQueryResult, TypeCountsQueryResult
from ons.search.paginator import Paginator


class DotDict(dict):
    """
    Simple class which wraps a dictionary and supports dot notation for setting values
    """
    def __init__(self, *args, **kwargs):
        super(DotDict, self).__init__(*args, **kwargs)

    def set_value(self, field_name, value):
        if field_name in self:
            self[field_name] = value
        elif "." in field_name:
            parts = field_name.split(".")
            if parts[0] == "description" and len(parts) <= 2:
                self["description"][parts[1]] = value
        else:
            raise Exception("Unable to set field %s" % field_name)


class ONSResponse(Response):

    def highlight_hits(self) -> List[DotDict]:
        """
        Checks response for highlighter fragments and applies them to each hit
        :return:
        """
        highlighted_hits = []

        hit: Hit
        for hit in self.hits:
            hit_dict = DotDict(hit.to_dict())
            if hasattr(hit, "meta") and isinstance(hit.meta, HitMeta):
                hit_meta: HitMeta = hit.meta

                # Check if highlighting results in the hit meta
                if hasattr(hit_meta, "highlight") and hasattr(hit_meta.highlight, "to_dict"):
                    highlight_dict = hit_meta.highlight.to_dict()

                    # Iterate over highlighted fields
                    for highlight_field in highlight_dict:
                        # Replace the _source field with the highlighted fragment, provided there is only one
                        if len(highlight_dict[highlight_field]) == 1:
                            highlighted_field = highlight_dict[highlight_field][0]

                            # Overwrite the _source field
                            hit_dict.set_value(highlight_field, highlighted_field)
                        else:
                            message = "Got multiple highlighted fragments, cowardly refusing to overwrite _source for " \
                                      "field '%s', fragments: %s" % (highlight_field, highlight_dict[highlight_field])
                            logging.debug(message)
            # Remap type field
            hit_dict["_type"] = hit_dict.pop("type", None)
            # Add the hit to the list
            highlighted_hits.append(hit_dict)

        return highlighted_hits

    def hits_to_json(self) -> List[DotDict]:
        """
        Converts the search hits to a list of JSON, with highlighting applied
        :return:
        """
        return self.highlight_hits()

    def to_type_counts_query_search_result(self) -> SearchResult:
        """
        Converts an Elasticsearch response into a TypeCountsQueryResult
        :param doc_counts:
        :return:
        """
        result: TypeCountsQueryResult = TypeCountsQueryResult(self.aggregations)
        return result

    def to_featured_result_query_search_result(self) -> SearchResult:
        """
        Converts an Elasticsearch response into a ContentQueryResult
        :return:
        """
        return self.to_content_query_search_result(1, 1, SortField.relevance)

    def to_departments_query_search_result(self, page_number: int, page_size: int) -> SearchResult:
        """
        Converts an Elasticsearch response into a ContentQueryResult. Note, for a departments query the only
        possible sort option is by relevence.
        :param page_number:
        :param page_size:
        :param sort_by:
        :return:
        """
        return self.to_content_query_search_result(page_number, page_size, SortField.relevance)

    def to_content_query_search_result(self, page_number: int, page_size: int, sort_by: SortField) -> SearchResult:
        """
        Converts an Elasticsearch response into a ContentQueryResult
        :param page_number:
        :param page_size:
        :param sort_by:
        :return:
        """
        hits = self.hits_to_json()

        paginator = Paginator(
            self.hits.total,
            page_number,
            result_per_page=page_size)

        result: ContentQueryResult = ContentQueryResult(
            self.hits.total,
            self.took,
            hits,
            paginator,
            sort_by
        )

        return result
