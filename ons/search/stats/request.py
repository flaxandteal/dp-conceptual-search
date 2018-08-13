import abc


class Request(abc.ABC):
    def __init__(self, host, uri):
        self._host = host
        self._uri = uri

    def target(self, query, page):
        return self._host + self._uri + "?q=" + query + "&page=%d" % page

    def search(self, query, page=1):
        import requests

        r = requests.get(self.target(query, page))
        return r.json()

    def find_hit_for_query(self, query, uri):
        page = 1
        while True:
            hits: list = self.get_hits(query, page)
            if uri in hits:
                return page, hits.index(uri) + 1
            else:
                page += 1

    @staticmethod
    def rank(page: int, index: int, page_size: int = 10):
        return index + ((page - 1) * page_size)

    @abc.abstractmethod
    def get_hits(self, query, page: int):
        pass


class BabbageRequest(Request):
    host = "http://localhost:20000/"
    uri = "search/data"

    def __init__(self):
        super(BabbageRequest, self).__init__(self.host, self.uri)

    def target(self, query, page):
        return self._host + self._uri + "?q=" + query + \
            "&page=%d" % page + "&searchTarget=internal"

    def get_hits(self, query, page):
        response = self.search(query, page=page)
        hits = []
        for hit in response['result']['results']:
            hits.append(hit.get('uri'))

        return hits


class SearchRequest(Request):
    host = "http://localhost:5000/"
    uri = "search/ons/content"

    def __init__(self):
        super(SearchRequest, self).__init__(self.host, self.uri)

    def get_hits(self, query, page):
        response = self.search(query, page=page)
        hits = []
        for hit in response['results']:
            hits.append(hit.get('uri'))

        return hits


class ConceptualSearchRequest(SearchRequest):
    uri = "search/conceptual/ons/content"
