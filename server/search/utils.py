from ons.search.sort_fields import SortFields
from ons.search.search_engine import AbstractSearchClient


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
    from ons.search.response import ONSResponse

    if inspect.isawaitable(responses):
        responses = await responses

    result = {}
    for search, response in responses:
        assert isinstance(
            search, AbstractSearchClient), "Expected instance of BaseSearchEngine, got %s" % type(search)

        assert isinstance(
            response, ONSResponse), "Expected instance of ONSResponse, got %s" % type(response)

        if hasattr(
                response,
                "aggregations") and hasattr(
                response.aggregations,
                "docCounts"):
            result["counts"] = response.aggs_to_json()
        elif search.query_size == 1:
            # Featured result query
            featured_result_hits = [h.to_dict()
                                    for h in response.hits]

            result["featuredResult"] = {
                "numberOfResults": len(featured_result_hits),
                "results": featured_result_hits
            }
        else:
            result["result"] = response.hits_to_json(
                page_number, page_size, sort_by=sort_by)

    return result
