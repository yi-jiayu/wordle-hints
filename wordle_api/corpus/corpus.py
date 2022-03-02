from collections import Counter
from dataclasses import dataclass


@dataclass
class WordFilter:
    letter: str
    positions: list[int]
    exclude_positions: list[int]
    at_least: int
    at_most: int

    def __post_init__(self):
        self.letter = self.letter.upper().strip()


class WordCorpus:
    def __init__(self, words: set[str], source: str, word_length: int):
        if not (isinstance(word_length, int) and word_length > 0):
            raise ValueError("word length must be a positive integer")
        self._word_length = word_length
        self._source = source

        self._words: set[str] = {word for w in words if len(word := w.upper().strip()) == word_length}
        self._fixed_letter_map = FixedLetterMap(self._words, word_length)
        self._letter_count_map = LetterCountMap(self._words, word_length)

    def get_potential_words(self, filters: list[WordFilter]) -> set[str]:
        """
        Gets potential words given a filter list

        :param filters: a list of WordFilter to apply

        Examples
        --------
        >>> from corpus import CorpusFactory, WordFilter
        >>> corpus = CorpusFactory().get_corpus('web2')
        >>> # 'S' is the first letter, 'T' occurs twice but is not in the 3rd position, no 'E' in word
        >>> corpus.get_potential_words([WordFilter('s', positions=[1], exclude_positions=[], at_least=1, at_most=5),
        ...                             WordFilter('t', positions=[], exclude_positions=[3], at_least=2, at_most=5),
        ...                             WordFilter('e', positions=[], exclude_positions=[], at_least=0, at_most=0)])
        {'SCOTT', 'SHOTT', 'START', 'STILT', 'STINT', 'STITH', 'STOAT', 'STOOT', 'STOUT', 'STRIT', 'STRUT', 'STUNT', 'STURT'}
        """
        words = self.words.copy()

        # filter for possible words first
        for x in filters:
            for pos in x.positions:
                words &= self._fixed_letter_map.get(pos, x.letter)

            for pos in x.exclude_positions:
                words -= self._fixed_letter_map.get(pos, x.letter)

            if x.at_least > 0:
                words &= self._letter_count_map.get(x.letter, x.at_least, x.at_most)
            elif x.at_most == 0:
                words = {w for w in words if x.letter not in w}

        return words

    @property
    def word_length(self):
        return self._word_length

    @property
    def source(self):
        return self._source

    @property
    def words(self):
        return self._words.copy()

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


class FixedLetterMap:
    """
    FixedLetterMap is used to collect words where we know the fixed (absolute) location of a letter.
        # For example, if we know there is a letter "T" in the 3rd spot, we will call
        # `FixedLetterMap.get(3, 'T') to get all valid words`
    """

    def __init__(self, words: set[str], word_length: int):
        self._map: dict[int, dict[str, set[str]]] = {i + 1: {} for i in range(word_length)}
        # fixed_letter_position_map is used to collect words where we know the fixed (absolute)

        # populates the maps
        for word in words:
            for pos, letter in enumerate(word, 1):  # type: int, str
                if letter not in self._map[pos]:
                    self._map[pos][letter] = set()

                self._map[pos][letter].add(word)

    def get(self, position: int, letter: str):
        return self._map[position][letter]


class LetterCountMap:
    def __init__(self, words: set[str], word_length: int):
        self._word_length = word_length
        self._map: dict[str, dict[int, set[str]]] = {}

        for word in words:
            counts = Counter(word)
            for letter, num in counts.items():
                if letter not in self._map:
                    self._map[letter] = {}
                if num not in self._map[letter]:
                    self._map[letter][num] = set()

                self._map[letter][num].add(word)

    def get(self, letter: str, min_count: int, max_count: int):
        if not (0 < min_count <= max_count <= self._word_length):
            raise ValueError(f"letter '{letter}' min_count and max_count must be between [0, {self._word_length}] and min_count must be <= max_count. "
                             f"Got min_count={min_count} and max_count={max_count}")
        letter_count_map = self._map[letter]

        words = set()
        for i in range(min_count, max_count + 1):
            words |= letter_count_map.get(i, set())

        return words
