import os
import numpy as np

from core.search.stats.judgements import Judgements

MAX_SCORE = float(os.environ.get("MAX_SCORE", 4.0))


def ideal_gain(num: int):
    i = 0
    increment = (1.0 / (float(num) - 1.0)) * num

    ideal_gain_arr = np.zeros(num)
    val = len(ideal_gain_arr)
    while val > 0:
        ideal_gain_arr[i] = (val / float(num)) * MAX_SCORE
        i += 1
        val -= increment

    return ideal_gain_arr


def ideal_discounted_cumulative_gain(num: int, ideal_gain_arr: np.ndarray=None):
    if ideal_gain_arr is None:
        ideal_gain_arr = ideal_gain(num)

    ideal_discounted_cumulative_gain_arr = np.zeros(num)

    total = 0.0
    for i in range(num):
        total += ideal_gain_arr[i] / float(i + 1)
        ideal_discounted_cumulative_gain_arr[i] = total
    return ideal_discounted_cumulative_gain_arr


class NDCG(object):
    def __init__(self, judgements: Judgements):
        self.judgements = judgements

    def dcg(self):

        dcg_dict = {}
        for key in self.judgements:
            total = 0.0
            dcg_dict[key] = {"dcg": [], "urls": [], "rank": []}
            judgements = self.judgements[key]

            sorted_judgements = sorted(judgements.items(), key=lambda kv: kv[1]['rank'])
            for url, data in sorted_judgements:
                total += data["judgement"] / float(data["rank"])
                dcg_dict[key]["dcg"].append(total)
                dcg_dict[key]["urls"].append(url)
                dcg_dict[key]["rank"].append(data["rank"])

        return dcg_dict

    def ndcg(self):

        dcg_dict = self.dcg()
        ndcg_dict = {}

        for key in dcg_dict.keys():
            dcg_data = dcg_dict[key]
            dcg = dcg_data["dcg"]

            idcg = ideal_discounted_cumulative_gain(len(dcg))
            ndcg = np.zeros(len(dcg))

            for i in range(len(ndcg)):
                ndcg[i] = min(1.0, dcg[i] / idcg[i])

            ndcg_dict[key] = {}
            ndcg_dict[key]["ndcg"] = ndcg
            ndcg_dict[key]["urls"] = dcg_data["urls"]
            ndcg_dict[key]["rank"] = dcg_data["rank"]
        return ndcg_dict

    def __iter__(self):
        return self.judgements.__iter__()

    def __getitem__(self, i):
        return self.judgements[i]

    def __len__(self):
        return len(self.judgements)
