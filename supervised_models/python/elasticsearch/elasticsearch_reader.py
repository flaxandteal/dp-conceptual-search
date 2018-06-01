from typing import List
from elasticsearch import Elasticsearch
from supervised_models.python.page import Page
from supervised_models.python.reader import DocumentReader


def get_search_url() -> str:
    import os
    search_url = os.environ.get(
        'ELASTIC_SEARCH_SERVER',
        'http://localhost:9200')
    return search_url


class ElasticsearchReader(DocumentReader):
    def __init__(self, es_url: str=get_search_url()):
        self.client = Elasticsearch(es_url)

    def indices_exist(self, index):
        return self.client.indices.exists(index=index)

    def load_pages(self, index: str='ons*', size: int=1000, body: dict={}) -> List[Page]:
        pages = []

        # Process hits here
        def process_hits(hits):
            for item in hits:
                pages.append(Page(item["_source"]))

        # Check index exists
        if not self.indices_exist(index):
            print("Index " + index + " does not exist")
            exit()

        # Init scroll by search
        data = self.client.search(
            index=index,
            # doc_type=doc_type,
            scroll='2m',
            size=size,
            body=body
        )

        # Get the scroll ID
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])

        # Before scroll, process current batch of hits
        process_hits(data['hits']['hits'])

        while scroll_size > 0:
            "Scrolling..."
            data = self.client.scroll(scroll_id=sid, scroll='2m')

            # Process current batch of hits
            process_hits(data['hits']['hits'])

            # Update the scroll ID
            sid = data['_scroll_id']

            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])

        return pages
