from elasticsearch_dsl.response import Response
from elasticsearch_dsl.response.hit import Hit, HitMeta

from typing import List

from ons.search.sort_fields import SortFields


class SimpleHit(dict):
    def __init__(self, *args, **kwargs):
        super(SimpleHit, self).__init__(*args, **kwargs)

    def set_value(self, field_name, value):
        if field_name in self:
            self[field_name] = value
        elif "." in field_name:
            parts = field_name.split(".")
            if parts[0] == "description" and len(parts) <= 2:
                self["description"][parts[1]] = value
        else:
            raise Exception("Unable to set field %s" % field_name)


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
        if not isinstance(current_data, dict):
            break
    return current_data


def highlight(highlighted_text: str, val: str, tag: str='strong') -> str:
    """
    Wraps the desired text snippet in :param tag html tags.
    :param highlighted_text:
    :param val:
    :param tag:
    :return:
    """
    tag_start = '<%s>' % tag
    tag_end = '</%s>' % tag

    tokens = val.split()

    for i in range(len(tokens)):
        if not tokens[i].startswith(
                tag_start) and highlighted_text in tokens[i]:
            tokens[i] = "{tag_start}{token}{tag_end}".format(
                tag_start=tag_start, token=tokens[i], tag_end=tag_end)

    return " ".join(tokens)


def marshall_hits(hits: List[Hit]) -> list:
    """
    Converts Elasticsearch hits into a valid JSON response.
    :param hits:
    :return:
    """
    import re
    from ons.search import fields

    hits_list = []
    for hit in hits:
        hit_dict = SimpleHit(hit.to_dict())
        if hasattr(hit, "meta"):
            meta: HitMeta = hit.meta
            if hasattr(meta, "highlight"):
                highlight_dict = meta.highlight.to_dict()
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
                                if highlight_key == fields.keywords_raw.name:
                                    highlight_key = fields.keywords.name
                                hit_dict.set_value(highlight_key, highlighted_vals)

            # set _type field
            hit_dict["_type"] = meta.doc_type
            hit_dict["_meta"] = meta.to_dict()
            hits_list.append(hit_dict)
    return hits_list


class ONSResponse(Response):
    """
    Class for marshalling Elasticsearch results to JSON expected by babbage
    """

    def featured_result_to_json(self) -> dict:
        return self.response_to_json(1, 1)

    def aggs_to_json(self) -> dict:
        """
        Returns search aggregations as formatted JSON.
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

        return {}

    def hits_to_json(self):
        """
        Returns search hits only as formatted JSON.
        :return:
        """
        from ons.search.paginator import RESULTS_PER_PAGE

        return self.response_to_json(0, RESULTS_PER_PAGE)

    def response_to_json(self, page_number: int, page_size: int,
                         sort_by: SortFields=SortFields.relevance) -> dict:
        """
        Builds and returns the full JSON response expected by Babbage.
        :return:
        """
        from ons.search.paginator import Paginator, MAX_VISIBLE_PAGINATOR_LINK

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
