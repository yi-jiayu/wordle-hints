import io
import operator
import pickle
import zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm


class CorpusFactory:
    __data_source__ = {
        'coca': {
            'home': 'corpusdata',
            'url': 'https://www.corpusdata.org/coca/samples/coca-samples-wlp.zip',
        },
        'coha': {
            'home': 'corpusdata',
            'url': 'https://www.corpusdata.org/coha/samples/wordLemPoS.zip',
        },
        'glowbe': {
            'home': 'corpusdata',
            'url': 'https://www.corpusdata.org/glowbe/samples/wordLemPoS.zip',
        },
        'now': {
            'home': 'corpusdata',
            'url': 'https://www.corpusdata.org/now/samples/wordLemPos.zip',
        },
        'corona': {
            'home': 'corpusdata',
            'url': 'https://www.corpusdata.org/corona/samples/wordLemPoS.zip',
        },
        'wiki': {
            'home': 'corpusdata',
            'url': 'https://www.corpusdata.org/wiki/samples/wordLemPoS.zip',
        },
        'tv': {
            'home': 'corpusdata',
            'url': 'https://www.corpusdata.org/tv/samples/tv-wlp.zip',
        },
        'movies': {
            'home': 'corpusdata',
            'url': 'https://www.corpusdata.org/movies/samples/movies-wlp.zip',
        },
        'soap': {
            'home': 'corpusdata',
            'url': 'https://www.corpusdata.org/soap/samples/soap-wlp.zip',
        },
        'web2': {
            'home': 'freebsd',
            'url': [
                'https://svnweb.freebsd.org/base/head/share/dict/web2?revision=326913',
                'https://svnweb.freebsd.org/base/head/share/dict/web2a?revision=180208',
            ]
        }
    }

    def __init__(self, word_length=5):
        """
        A factory to create corpus

        Examples
        --------
        >>> from data_source import CorpusFactory
        >>> factory = CorpusFactory(5)
        >>> corpus = factory.get_corpus('web2')
        >>> corpus
        WordCorpus(source='web2', word_length=5, words={'LEPER', 'REPOT', 'JUTTY', 'GAUMY', 'AMBRY', ...})
        """
        self._word_length = word_length

    @property
    def sources(self):
        return list(self.__data_source__)

    @staticmethod
    def _get_cache_folder(source: str):
        cache_folder = Path.home() / ".wordle" / source
        cache_folder.mkdir(mode=0o666, parents=True, exist_ok=True)

        return cache_folder

    def get_corpus(self, source='web2', reload_source=False, reload_corpus=False):
        """Gets the corpus object"""
        assert source in self.__data_source__, f"{source} is not a valid corpus source. Use one of {tuple(self.__data_source__.keys())}"
        file_location = self._get_cache_folder(source) / f'length_{self._word_length}.p'

        if not file_location.exists() or reload_source or reload_corpus:
            words = self.get_corpus_source(source, reload_source)
            corpus = WordCorpus(words, source, self._word_length)
            with open(file_location, 'wb') as f:
                pickle.dump(corpus, f)

            return corpus
        else:
            with open(file_location, 'rb') as f:
                return pickle.load(f)

    def get_corpus_source(self, source: str, reload_source=False) -> set[str]:
        """Gets the corpus's full word set. Downloads from source if it does not exist in cache"""
        cache_folder = self._get_cache_folder(source)
        source_file = cache_folder / 'source.p'

        if source_file.exists() and not reload_source:
            with open(source_file, 'rb') as f:
                return pickle.load(f)
        else:
            details = self.__data_source__[source]
            match home := details['home']:
                case 'freebsd':
                    urls = details['url']
                    words = set()
                    for url in urls:
                        resp = requests.get(url)
                        words |= {word for w in resp.text.split('\n') if (word := w.strip().upper()).isalpha()}

                case 'corpusdata':
                    url = details['url']
                    resp = requests.get(url)

                    if not resp.ok:
                        raise requests.exceptions.RequestException(f"Could not get corpus data from: {url}")

                    words = set()
                    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                        for info in zf.infolist():
                            if info.filename.endswith('.txt'):
                                for line in zf.open(info).readlines():
                                    for word in line.split(b'\t'):
                                        try:
                                            word = word.upper().strip()
                                            if word.isalpha():
                                                words.add(word.decode())
                                        except UnicodeEncodeError:
                                            pass
                case _:
                    raise ValueError(f"invalid source home: '{home}'")

            with open(source_file, 'wb') as f:
                pickle.dump(words, f)

            return words

    def recreate_corpus(self, reload_source=True, reload_corpus=True):
        """
        Recreates all the corpus and stash the results

        Examples
        --------
        >>> from data_source import CorpusFactory
        >>> factory = CorpusFactory(5)
        >>> factory.recreate_corpus(reload_source=False)  # doctest: +SKIP
        """
        total = len(self.sources)
        with ThreadPoolExecutor(total) as pool, tqdm(desc="Creating Corpus", total=total) as bar:
            futures = [pool.submit(self.get_corpus, source=source, reload_source=reload_source, reload_corpus=reload_corpus) for source in self.sources]
            for _ in as_completed(futures):
                bar.update()


class WordCorpus:
    def __init__(self, words: set[str], source: str, word_length: int):
        assert isinstance(word_length, int) and word_length > 0, "word length must be a positive integer"
        self._word_length = word_length
        self._source = source

        self._words = {word for w in words if len(word := w.upper().strip()) == word_length}

        self._contains_letter_map: dict[str, set[str]] = defaultdict(set)
        # contains letter map is used to grab all words which contains a particular letter regardless of the letter's location

        self._fixed_letter_position_map: dict[int, dict[str, set[str]]] = defaultdict(self._default_fixed_letter_position_map)
        # fixed_letter_position_map is used to collect words where we know the fixed (absolute) location of a letter.
        # For example, if we know there is a letter "T" in the 3rd spot, we will call
        # `corpus._fixed_letter_position_map[3]['T'] to get all valid words`

        # populates the maps
        for word in self._words:  # type: str
            for i, letter in enumerate(word, 1):  # type: int, str
                self._fixed_letter_position_map[i][letter].add(word)
                self._contains_letter_map[letter].add(word)

        # creates the ranking for each word, so that we can sort according to best guess later
        # ranking works by frequency of occurrence
        self._rankings = WordRanking(self._words, self._fixed_letter_position_map)

    @property
    def rankings(self):
        return self._rankings

    def get_initial_guesses(self, top_n=10):
        return self.rankings.get_initial_guess(top_n)

    def get_potential_words(self,
                            fixed_letters: dict[int, str] = None,
                            include_letters: list[str] = None,
                            exclude_letters: list[str | tuple[str, list[int]]] = None,
                            discount_repeated_letters_when_sorting=True) -> pd.DataFrame:
        """
        Gets a list of potential words

        :param fixed_letters: A dictionary where the key is the letter position and the value is the letter.
        :param include_letters: A list of letters to include
        :param exclude_letters: A list of letters to exclude. If in tuple form, the first value is the letter and the second value is a list of integer
                                positions to exclude. So ('S', [1, 4]) means to exclude all words where 'S' is in the 1st and 4th position
        :param discount_repeated_letters_when_sorting: When creating the ranking sort, words with repeated letters (i.e. seeks) have discounted scores

        Example
        -------
        >>> from data_source import CorpusFactory
        >>> factory = CorpusFactory(5)
        >>> corpus = factory.get_corpus('web2')
        >>> corpus.get_potential_words({1: 'S', 3: 'I'}, include_letters=['S'], exclude_letters=['A', 'R', ('E', [2, 5])])
             WORD    SCORE
        0   SOILY  6912000
        1   SUINT  6375600
        2   SHINY  5961600
        3   SUITY  5745600
        4   SHIEL  5335200
        ..    ...      ...
        70  SKIDI    67200
        71  SPIFF    63000
        72  SKIFF    33600
        73  SHISH    10800
        74  SWISS     6600
        """
        words = self.words
        if fixed_letters:
            for i, letter in fixed_letters.items():
                words &= self._fixed_letter_position_map[i][letter.upper()]

        if include_letters:
            for letter in include_letters:
                words &= self._contains_letter_map[letter.upper()]

        if exclude_letters:
            for letter in exclude_letters:
                if isinstance(letter, str):
                    words -= self._contains_letter_map[letter.upper()]
                elif isinstance(letter, tuple):
                    letter, positions = letter  # type: str, list[int]
                    for pos in positions:
                        words -= self._fixed_letter_position_map[pos][letter.upper()]

        if len(words) == 0:
            return pd.DataFrame(columns=['WORD', 'SCORE'])

        potential_words = pd.DataFrame({'WORD': list(words)})
        potential_words['SCORE'] = potential_words['WORD'].map(self.rankings.get_rankings(discount_repeated_letters_when_sorting))
        potential_words = potential_words.sort_values(['SCORE'], ascending=False).reset_index(drop=True)

        return potential_words

    @property
    def word_length(self):
        return self._word_length

    @property
    def source(self):
        return self._source

    @property
    def words(self):
        return self._words

    def __len__(self):
        return len(self._words)

    def __contains__(self, word: str):
        return word.upper().strip() in self._words

    def __repr__(self):
        words = list(self._words)
        if len(words) > 5:
            words_repr = f"{{{', '.join(repr(w) for w in words[:5])}, ...}}"
        else:
            words_repr = f"{{{', '.join(repr(w) for w in words)}}}"

        return f"{self.__class__.__name__}(source='{self.source}', word_length={self.word_length}, words={words_repr})"

    def __str__(self):
        return self.__repr__()

    ####################################################
    # methods below are used to bypass pickling issues #
    ####################################################

    @staticmethod
    def _default_fixed_letter_position_map():
        return defaultdict(set)


@dataclass
class InitialWordRanking:
    score: int
    letters: str
    words: list[str]


class WordRanking:
    def __init__(self, words: set[str], fixed_letter_position_map: dict[int, dict[str, set[str]]]):
        # sorting words for initial guesses. This is different from the rest
        self._letter_frequency_ranking = self._create_letter_frequency_ranking(words)

        raw_rankings = self._create_raw_rankings(fixed_letter_position_map)
        self._rankings = {
            'standard': {word: self._score_word(letter_score) for word, letter_score in raw_rankings.items()},
            'discounted': {word: self._score_word(letter_score, discount_repeated_letters=True) for word, letter_score in raw_rankings.items()},
        }

    @staticmethod
    def _create_raw_rankings(fixed_letter_position_map):
        rankings = defaultdict(list)
        for pos, word_sets in fixed_letter_position_map.items():
            # this sorts the letter_set in the current position from shortest (least words) to longest (most words)
            set_and_score = defaultdict(list)  # the keys are the magnitude score
            for letter, word_set in word_sets.items():
                set_and_score[len(word_set)].append(word_set)

            # we reduce the score down to frequency, irrespective of magnitude. For sets with the same number of occurrences,
            # we take the average ranking
            for rank, score in enumerate(sorted(set_and_score), 1):
                for word_set in set_and_score[score]:
                    for word in word_set:
                        rankings[word].append((word[pos - 1], rank))
        return rankings

    @staticmethod
    def _score_word(letter_score: list[tuple[str, int]], discount_repeated_letters=False):
        scores = {}
        for letter, ranking in letter_score:
            if discount_repeated_letters and letter in scores and ranking < scores[letter]:
                continue
            scores[letter] = ranking

        start = 1
        for v in scores.values():
            start *= v
        return start

    def _create_letter_frequency_ranking(self, words: set[str]):
        letter_count = defaultdict(int)
        for word in words:
            for letter in set(word):
                letter_count[letter] += 1

        rankings = {word: self._score_word([(letter, letter_count[letter]) for letter in word]) for word in words}

        initial_rankings = {}
        for word, score in sorted(rankings.items(), key=operator.itemgetter(1), reverse=True):
            key = ''.join(sorted(set(word)))  # anagram letter set
            if key not in initial_rankings:
                initial_rankings[key] = InitialWordRanking(score, key, [])
            initial_rankings[key].words.append(word)

        output = []
        for i, x in enumerate(sorted(initial_rankings.values(), key=operator.attrgetter('score')), start=1):
            x.score = i
            output.append(x)
        output.reverse()
        return output

    def get_initial_guess(self, top_n=10):
        assert isinstance(top_n, int) and (top_n > 0 or top_n == -1), 'top_n must be a positive integer or -1'
        if top_n > 0:
            return self._letter_frequency_ranking[:top_n]
        return self._letter_frequency_ranking

    def get_rankings(self, discount_repeated_letters=False) -> dict[str, int]:
        return self._rankings['discounted' if discount_repeated_letters else 'standard']


if __name__ == '__main__':
    print("Creating all corpus")
    CorpusFactory().recreate_corpus()
