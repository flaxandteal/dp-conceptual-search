from . import fields
from elasticsearch_dsl import query


def _get_field_name(field):
    if isinstance(field, fields.Field):
        return field.name
    return field


def match(field, search_term, **kwargs):
    field_name = _get_field_name(field)

    query_dict = {
        field_name: {
            "query": search_term,
        }
    }

    for item in kwargs:
        query_dict[field_name][item] = kwargs[item]

    q = query.Match(**query_dict)
    return q


def multi_match(field_list, search_term, **kwargs):
    if hasattr(field_list, "__iter__") is False:
        field_list = [field_list]

    formatted_field_list = []
    for field in field_list:
        field_name = _get_field_name(field)
        formatted_field_list.append(field_name)

    query_dict = {
        "query": search_term,
        "fields": formatted_field_list,
    }

    for item in kwargs:
        query_dict[item] = kwargs[item]

    q = query.MultiMatch(**query_dict)
    return q


def content_query(search_term, function_scores=None, compute_additional_keywords=False):
    """
    Returns the default ONS content query

    :param search_term:
    :param function_scores:
    :param compute_additional_keywords:
    :return:
    """
    q = query.DisMax(
        queries=[
            query.Bool(
                should=[
                    match(fields.title_no_dates, search_term, type="boolean", boost=10.0,
                          minimum_should_match="1<-2 3<80% 5<60%"),
                    match(fields.title_no_stem, search_term, type="boolean", boost=10.0,
                          minimum_should_match="1<-2 3<80% 5<60%"),
                    multi_match([fields.title.field_name_boosted, fields.edition.field_name_boosted], search_term,
                                type="cross_fields", minimum_should_match="3<80% 5<60%")
                ]
            ),
            multi_match([fields.summary.name, fields.metaDescription.name], search_term,
                        type="best_fields", minimum_should_match="75%"),
            match(fields.keywords, search_term, type="boolean", operator="AND"),
            multi_match([fields.cdid.name, fields.datasetId.name], search_term),
            match(fields.searchBoost, search_term, type="boolean", operator="AND", boost=100.0)
        ]
    )

    if compute_additional_keywords:
        from ..word_embedding.supervised_models import SupervisedModels, load_model
        model = load_model(SupervisedModels.ONS)

        search_vector = model.get_sentence_vector(search_term)
        additional_keywords, similarity = model.get_labels_for_vector(search_vector, 10)
        additional_keywords = [k.replace("_", " ") for k in additional_keywords]

        # Add query to dis_max
        keywords_query = query.Bool(should=[query.Match(**{fields.keywords.name: k}) for k in additional_keywords])

        q_dict = q.to_dict()
        q_dict["dis_max"]["queries"].append(keywords_query.to_dict())

        q = query.DisMax(**q_dict["dis_max"])

    if function_scores is None:
        return q
    else:
        return query.FunctionScore(query=q, functions=function_scores)


def type_counts_query():
    type_count_query = {
        "docCounts": {
            "terms": {
                "field": "_type"
            }
        }
    }

    return type_count_query
