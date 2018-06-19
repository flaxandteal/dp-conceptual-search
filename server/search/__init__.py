from server.search.hit import Hit
from server.search.sort_by import SortOrder, SortFields
from server.search.search_engine import BaseSearchEngine
from server.search.paginator import Paginator, MAX_VISIBLE_PAGINATOR_LINK


def buckets_to_json(buckets) -> (dict, int):
    total = 0

    result = {}
    for item in buckets:
        item_key = item["key"]
        count = item["doc_count"]
        result[item_key] = count
        total += count

    return result, total


def get_var(input_dict: dict, accessor_string: str):
    """Gets data from a dictionary using a dotted accessor-string"""
    current_data = input_dict
    for chunk in accessor_string.split('.'):
        current_data = current_data.get(chunk, {})
    return current_data


def _highlight(highlighted_text: str, val: str, tag: str='strong') -> str:
    if highlighted_text in val:
        idx = val.index(highlighted_text)
        tag_start = '<%s>' % tag
        tag_end = '</%s>' % tag
        tag_start_length = len(tag_start)
        if val[idx-tag_start_length:idx] != tag_start:
            val = val.replace(
                highlighted_text,
                "%s%s%s" % (tag_start, highlighted_text, tag_end))
    return val


def marshall_hits(hits) -> list:
    """
    Substitues highlights into fields and returns valid JSON
    :param hits:
    :return:
    """
    import re

    hits_list = []
    for hit in hits:
        hit_dict = Hit(hit.to_dict())
        if hasattr(hit.meta, "highlight"):
            highlight_dict = hit.meta.highlight.to_dict()
            for highlight_key in highlight_dict:
                for fragment in highlight_dict[highlight_key]:
                    fragment = fragment.strip()
                    if "<strong>" in fragment and "</strong>" in fragment:
                        highlighted_text = " ".join(re.findall(
                            "<strong>(.*?)</strong>", fragment))

                        val = get_var(hit_dict, highlight_key)

                        if isinstance(val, str):
                            hit_dict.set_value(
                                highlight_key, _highlight(
                                    highlighted_text, val))
                        elif hasattr(val, "__iter__"):
                            highlighted_vals = []
                            for v in val:
                                highlighted_vals.append(
                                    _highlight(highlighted_text, v))
                            hit_dict.set_value(highlight_key, highlighted_vals)

        # set _type field
        hit_dict["_type"] = hit.meta.doc_type
        hits_list.append(hit_dict)
    return hits_list


async def hits_to_json(
        responses,
        page_number: int,
        page_size: int,
        sort_by: SortFields=SortFields.relevance) -> dict:
    """
    Replicates the JSON response of Babbage
    :return:
    """
    import inspect

    if inspect.isawaitable(responses):
        responses = await responses

    result = {}
    for search, response in responses:
        assert isinstance(
            search, BaseSearchEngine), "Expected instance of BaseSearchEngine, got %s" % type(search)
        if hasattr(
                response,
                "aggregations") and hasattr(
                response.aggregations,
                "docCounts"):
            aggs = response.aggregations.__dict__["_d_"]["docCounts"]
            buckets = aggs["buckets"]
            if len(buckets) > 0:
                # Type counts query
                aggregations, total_hits = buckets_to_json(buckets)

                result["counts"] = {
                    # "numberOfResults": response.hits.total,
                    "numberOfResults": total_hits,
                    "docCounts": aggregations
                }
        elif search.query_size == 1:
            # Featured result query
            featured_result_hits = [h.to_dict()
                                    for h in response.hits]

            result["featuredResult"] = {
                "numberOfResults": len(featured_result_hits),
                "results": featured_result_hits
            }
        else:
            # Content query - Init Paginator
            paginator = Paginator(
                response.hits.total,
                MAX_VISIBLE_PAGINATOR_LINK,
                page_number,
                page_size)

            result["result"] = {
                "numberOfResults": response.hits.total,
                "took": response.took,
                "results": marshall_hits(response.hits),
                "docCounts": {},
                "paginator": paginator.to_dict(),
                "sortBy": sort_by.name
            }

    return result
