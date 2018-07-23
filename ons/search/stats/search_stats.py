import pymongo

from core.search.stats.judgements import Judgements


class SearchStats(object):
    db = "local"
    collection = "searchstats"

    def __init__(self, conceptual_search: bool=False):
        self._client = pymongo.MongoClient()
        self._db = self._client.get_database(self.db)
        self._collection = self._db.get_collection(self.collection)

        self._docs = []

        self.conceptual_search = conceptual_search
        self._load(self.conceptual_search)

    def _load(self, conceptual_search: bool):
        if len(self._docs) == 0:
            for doc in self._collection.find():
                if "conceptualsearch" in doc and doc.get("conceptualsearch") == conceptual_search:
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
            rank = doc.get("linkindex") + ((doc.get("pageindex") - 1) * doc.get("pagesize"))
            term = doc.get("term")
            url = doc.get('url')

            judgements.increment(term, url, rank)

        # Normalise
        judgements.normalise(max_judgement=max_judgement)

        return judgements
