import io
import os
import pickle
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

from .corpus import WordCorpus


class CorpusFactory:
    __corpus_instances__: dict[str, WordCorpus] = {}

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
        >>> from corpus import CorpusFactory
        >>> factory = CorpusFactory(5)
        >>> corpus = factory.get_corpus('web2')
        >>> corpus
        WordCorpus(source='web2', word_length=5, words={'BARON', 'PHORA', 'HOOEY', 'KOYAN', 'FEEZE', ...})
        """
        self._word_length = word_length

    @property
    def sources(self):
        return list(self.__data_source__)

    @staticmethod
    def _get_cache_folder(*paths: str):
        cache_folder = Path(os.getenv('WORDLE_FOLDER', Path.home())) / ".wordle"
        if paths:
            cache_folder = cache_folder.joinpath(*paths)

        if not cache_folder.exists():
            cache_folder.mkdir(mode=0o666, parents=True)

        return cache_folder

    def get_corpus(self, source='web2'):
        """Gets the corpus object"""
        if source in self.__corpus_instances__:
            return self.__corpus_instances__[source]

        assert source in self.__data_source__, f"{source} is not a valid corpus source. Use one of {tuple(self.__data_source__.keys())}"
        file_location = self._corpus_pickle_filepath(source)

        if not file_location.exists():
            corpus = self.create_corpus(source)
        else:
            with open(file_location, 'rb') as f:
                corpus = pickle.load(f)

        self.__corpus_instances__[source] = corpus
        return corpus

    def get_corpus_source(self, source: str) -> set[str]:
        """Gets the corpus's full word set. Downloads from source if it does not exist in cache"""
        source_file = self._corpus_source_filepath(source)

        if source_file.exists():
            with open(source_file, 'rb') as f:
                return pickle.load(f)
        else:
            return self.download_corpus_source(source)

    @lru_cache(maxsize=1)
    def get_word_frequency_table(self) -> pd.DataFrame:
        """Gets the word frequency table"""
        return pd.read_pickle(self._word_frequency_table_filepath())

    def recreate_data_files(self, reload_source=True, reload_corpus=True, reload_frequency=True):
        """
        Recreates all data files such as the source word list, frequency counts, corpus and stash the results

        Examples
        --------
        >>> from corpus import CorpusFactory
        >>> factory = CorpusFactory(5)
        >>> factory.recreate_data_files(reload_source=False)  # doctest: +SKIP
        """
        total = len(self.sources)

        with ThreadPoolExecutor(total) as pool:
            if reload_source:
                with tqdm(desc="Reloading source", total=total) as bar:
                    futures = [pool.submit(self.download_corpus_source, source=s) for s in self.sources]
                    for future in as_completed(futures):
                        if (err := future.exception()) is not None:
                            raise err
                        bar.update()

            if reload_corpus:
                with tqdm(desc="Creating Corpus", total=total) as bar:
                    futures = [pool.submit(self.create_corpus, source=s) for s in self.sources]
                    for future in as_completed(futures):
                        if (err := future.exception()) is not None:
                            raise err
                        bar.update()

            if reload_frequency:
                print("Reloading frequency table")
                self.download_word_frequencies()

    def download_corpus_source(self, source: str):
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

        with open(self._corpus_source_filepath(source), 'wb') as f:
            pickle.dump(words, f)

        return words

    def _corpus_source_filepath(self, source: str):
        return self._get_cache_folder(source) / 'source.p'

    def _corpus_pickle_filepath(self, source: str):
        return self._get_cache_folder(source) / f'length_{self._word_length}.p'

    def _word_frequency_table_filepath(self):
        return self._get_cache_folder() / "word_frequency.p"

    def create_corpus(self, source: str):
        words = self.get_corpus_source(source)

        corpus = WordCorpus(words, source, self._word_length)
        fp = self._corpus_pickle_filepath(source)
        with open(fp, 'wb') as f:
            pickle.dump(corpus, f)

        return corpus

    def download_word_frequencies(self):
        url = "https://github.com/hermitdave/FrequencyWords/raw/master/content/2018/en/en_full.txt"
        resp = requests.get(url)
        if not resp.ok:
            raise requests.exceptions.RequestException(f"Could not get word frequency data from: {url}")

        data = pd.DataFrame([line.split(' ') for line in resp.text.split('\n') if line], columns=['word', 'frequency'])
        data['frequency'] = data['frequency'].astype(int)

        data = (data[data['word'].str.fullmatch(r'\w+')]
                .sort_values('frequency', ascending=False)
                .reset_index(drop=True))

        data.to_pickle(self._word_frequency_table_filepath())
        return data
