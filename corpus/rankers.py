from collections import Counter

import pandas as pd


class WordRanker:
    def __init__(self, word_length: int, frequency_table: pd.DataFrame):
        self._word_length = word_length
        self._frequency = (frequency_table[frequency_table['word'].str.len() == 5]
                           .set_index('word')['frequency']
                           .rename(index=str.upper)
                           .to_dict())

    def partition_score(self, words: set[str]):
        _scores = {w: 1 for w in words}

        for i in range(self._word_length):
            pos_score = pd.Series(Counter([w[i] for w in words])).rank()
            for w in words:
                _scores[w] *= pos_score[w[i]]

        scores: pd.DataFrame = (pd.Series(_scores)
                                .rank()
                                .astype(int)
                                .rename_axis('word')
                                .rename('partition')
                                .reset_index())

        scores['frequency'] = scores['word'].map(self._frequency).fillna(0).astype(int)
        return scores.sort_values(['frequency', 'partition'], ascending=False).reset_index(drop=True)
