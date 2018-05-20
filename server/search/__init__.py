from .hit import Hit
from .sort_by import SortOrder
from .paginator import Paginator, MAX_VISIBLE_PAGINATOR_LINK

from elasticsearch_dsl.response import Response


def aggs_to_json(aggregations: dict, key: str) -> (dict, int):
    total = 0
    if key in aggregations:
        aggs = aggregations.__dict__["_d_"][key]
        buckets = aggs["buckets"]

        result = {}
        for item in buckets:
            item_key = item["key"]
            count = item["doc_count"]
            result[item_key] = count
            total += count

        return result, total
    return {}, total


def get_var(input_dict: dict, accessor_string: str):
    """Gets data from a dictionary using a dotted accessor-string"""
    current_data = input_dict
    for chunk in accessor_string.split('.'):
        current_data = current_data.get(chunk, {})
    return current_data


def _highlight(highlighted_text: str, val: str) -> str:
    val = val.replace(
        highlighted_text,
        "<strong>%s</strong>" % highlighted_text)

    val = val.replace(
        highlighted_text.lower(),
        "<strong>%s</strong>" % highlighted_text.lower())
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

        # rename 'type' field to '_type'
        hit_dict["_type"] = hit_dict.pop("type")
        hits_list.append(hit_dict)
    return hits_list


async def hits_to_json(
        content_response: Response,
        type_counts_response: Response,
        page_number: int,
        page_size: int,
        sort_by: str,
        featured_result_response: Response=None) -> dict:
    """
    Replicates the JSON response of Babbage
    :param content_response:
    :param type_counts_response:
    :param sort_by:
    :param featured_result_response:
    :return:
    """
    import inspect

    # Await content response
    if inspect.isawaitable(content_response):
        content_response = await content_response

    # Init Paginator
    paginator = Paginator(
        content_response.hits.total,
        MAX_VISIBLE_PAGINATOR_LINK,
        page_number,
        page_size)

    # Await type counts response
    if inspect.isawaitable(type_counts_response):
        type_counts_response = await type_counts_response

    # Format the output
    aggregations, total_hits = aggs_to_json(
        type_counts_response.aggregations, "docCounts")

    # Await featured result
    featured_result_hits = []
    if featured_result_response is not None:
        if inspect.isawaitable(featured_result_response):
            featured_result_response = await featured_result_response
        featured_result_hits = [h.to_dict()
                                for h in featured_result_response.hits]

    response = {
        "result": {
            "numberOfResults": content_response.hits.total,
            "took": content_response.took,
            "results": marshall_hits(content_response.hits),
            "docCounts": {},
            "paginator": paginator.to_dict(),
            "sortBy": sort_by

        },
        "counts": {
            "numberOfResults": content_response.hits.total,
            "docCounts": aggregations
        },
        "featuredResult": {
            "numberOfResults": len(featured_result_hits),
            "results": featured_result_hits
        },
    }

    return response
