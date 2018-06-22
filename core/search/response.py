from core.search.hit import Hit
from core.search.sort_by import SortFields

from elasticsearch_dsl.response import Response


def buckets_to_json(buckets) -> (dict, int):
    """
    Converts aggregation buckets to properly formatted JSON.
    :param buckets:
    :return:
    """
    total = 0

    result = {}
    for item in buckets:
        item_key = item["key"]
        count = item["doc_count"]
        result[item_key] = count
        total += count

    return result, total


def get_var(input_dict: dict, accessor_string: str):
    """
    Gets data from a dictionary using a dotted accessor-string
    :param input_dict:
    :param accessor_string:
    :return:
    """
    current_data = input_dict
    for chunk in accessor_string.split('.'):
        current_data = current_data.get(chunk, {})
    return current_data


def highlight(highlighted_text: str, val: str, tag: str='strong') -> str:
    """
    Wraps the desired text snippet in :param tag html tags.
    :param highlighted_text:
    :param val:
    :param tag:
    :return:
    """
    if highlighted_text in val:
        idx = val.index(highlighted_text)
        tag_start = '<%s>' % tag
        tag_end = '</%s>' % tag
        tag_start_length = len(tag_start)
        if val[idx - tag_start_length:idx] != tag_start:
            val = val.replace(
                highlighted_text,
                "%s%s%s" % (tag_start, highlighted_text, tag_end))
    return val


def marshall_hits(hits) -> list:
    """
    Converts Elasticsearch hits into a valid JSON response.
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
                                highlight_key, highlight(
                                    highlighted_text, val))
                        elif hasattr(val, "__iter__"):
                            highlighted_vals = []
                            for v in val:
                                highlighted_vals.append(
                                    highlight(highlighted_text, v))
                            hit_dict.set_value(highlight_key, highlighted_vals)

        # set _type field
        hit_dict["_type"] = hit.meta.doc_type
        hits_list.append(hit_dict)
    return hits_list


class ONSResponse(Response):
    """
    Class for marshalling Elasticsearch results to JSON expected by babbage
    """

    def aggs_to_json(self) -> dict:
        """

        :return:
        """
        if hasattr(self.aggregations, "docCounts"):
            aggs = self.aggregations.__dict__["_d_"]["docCounts"]
            buckets = aggs["buckets"]
            if len(buckets) > 0:
                # Type counts query
                aggregations, total_hits = buckets_to_json(buckets)

                json = {
                    # "numberOfResults": response.hits.total,
                    "numberOfResults": total_hits,
                    "docCounts": aggregations
                }

                return json

        return None

    def hits_to_json(self, page_number: int, page_size: int, sort_by: SortFields=SortFields.relevance) -> dict:
        """

        :return:
        """
        from core.search.paginator import Paginator, MAX_VISIBLE_PAGINATOR_LINK

        paginator = Paginator(
            self.hits.total,
            MAX_VISIBLE_PAGINATOR_LINK,
            page_number,
            page_size)

        json = {
            "numberOfResults": self.hits.total,
            "took": self.took,
            "results": marshall_hits(self.hits),
            "docCounts": {},
            "paginator": paginator.to_dict(),
            "sortBy": sort_by.name
        }

        return json
