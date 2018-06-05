test_document = {
    "_index": "ons1525855224872",
    "_type": "test",
    "_id": "/economy/inflationandpriceindices",
    "_score": 0.021380631,
    "_source": {
        "uri": "/economy/inflationandpriceindices",
        "type": "product_page",
                "description": {
                    "title": "Inflation and price indices",
                    "summary": "The rate of increase in prices for goods and services. Measures of inflation and prices include consumer price inflation, producer price inflation, the house price index, index of private housing rental prices, and construction output price indices. ",
                    "keywords": [
                        "Consumer Price Index,Retail Price Index,Producer Price Index,Services Producer Price Indices,Index of Private Housing Rental Prices,CPIH,RPIJ"],
                    "metaDescription": "The rate of increase in prices for goods and services. Measures of inflation and prices include consumer price inflation, producer price inflation, the house price index, index of private housing rental prices, and construction output price indices. ",
                    "unit": "",
                    "preUnit": "",
                    "source": ""
                },
        "searchBoost": []
    },
    "highlight": {
        "description.keywords": [" Price Index,<strong>Retail Price Index</strong>"]
    }
}

test_departments_document = {
    "_index": "departments",
    "_type": "test",
    "_id": "dfe",
    "_score": 5.461977,
    "_source": {
        "code": "dfe",
        "name": "The Department for Education",
        "url": "https://www.gov.uk/government/statistics?keywords=&topics%5B%5D=all&departments%5B%5D=department-for-education",
        "terms": [
            "DFE",
            "education",
            "A level",
            "degree",
            "NVQ",
            "school",
            "college",
            "university",
            "curriculum",
            "qualification",
            "teacher training",
            "pupil absence",
            "exclusions",
            "school workforce",
            "key stage",
            "higher education"]}}

test_aggs = {
    "doc_count_error_upper_bound": 0,
    "sum_other_doc_count": 0,
    "buckets": [
        {
            "key": "timeseries",
            "doc_count": 360
        },
        {
            "key": "article_download",
            "doc_count": 21
        },
        {
            "key": "bulletin",
            "doc_count": 16
        },
        {
            "key": "static_methodology_download",
            "doc_count": 4
        },
        {
            "key": "article",
            "doc_count": 3
        },
        {
            "key": "dataset_landing_page",
            "doc_count": 2
        },
        {
            "key": "static_foi",
            "doc_count": 1
        },
        {
            "key": "static_methodology",
            "doc_count": 1
        },
        {
            "key": "static_qmi",
            "doc_count": 1
        }
    ]
}
