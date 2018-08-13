import pymongo

from core.search.stats.judgements import Judgements

from ons.search.stats.request import Request


class SearchStats(object):
    db = "local"
    collection = "searchstats"

    def __init__(self):
        self._client = pymongo.MongoClient()
        self._db = self._client.get_database(self.db)
        self._collection = self._db.get_collection(self.collection)

        self._docs = []

        self._load()

    def _load(self):
        if len(self._docs) == 0:
            for doc in self._collection.find():
                self._docs.append(doc)

    def __len__(self):
        return len(self._docs)

    def __iter__(self):
        for doc in self._docs:
            yield doc

    def __getitem__(self, item):
        return self._docs[item]

    def group_by_search_term(self):
        grouped = {}

        for doc in self._docs:
            term = doc.get("term")

            if term not in grouped:
                grouped[term] = []
            grouped[term].append(doc)

        return grouped

    def judgements(self, max_judgement: float=4.0):
        """
        Groups searchStats by search term
        """
        judgements = Judgements()
        for doc in self._docs:
            rank = doc.get("linkindex") + \
                ((doc.get("pageindex") - 1) * doc.get("pagesize"))
            term = doc.get("term")
            url = doc.get('url')

            judgements.increment(term, url, rank)

        # Normalise
        judgements.normalise(max_judgement=max_judgement)

        return judgements

    def mock_judgements(self, request: Request, max_judgement=4.):
        judgements = self.judgements(max_judgement=max_judgement)

        for key in judgements:
            for uri in judgements[key]:
                page, index = request.find_hit_for_query(key, uri)
                new_rank = request.rank(page, index)
                judgements[key][uri]['rank'] = new_rank

        return judgements
