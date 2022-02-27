from corpus import CorpusFactory, WordRanker

WORD_LENGTH = 5
FACTORY = CorpusFactory(WORD_LENGTH)
RANKER = WordRanker(WORD_LENGTH, FACTORY.get_word_frequency_table())
