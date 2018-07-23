class Judgements(dict):

    def increment(self, term: str, url: str, rank: int):
        if term not in self:
            self[term] = {}

        if url not in self[term]:
            self[term][url] = {"count": 1, "rank": rank}
        else:
            self[term][url]["count"] += 1

    def normalise(self, max_judgement=4.0):
        import numpy as np

        for key in self:
            # Sort
            sorted_values = sorted(self[key].items(), key=lambda kv: kv[1]["count"])

            # Normalise
            j = np.linspace(0, max_judgement, len(sorted_values))
            for i, item in enumerate(sorted_values):
                k, v = item
                self[key][k]["judgement"] = j[i]
