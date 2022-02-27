from corpus import WordFilter
from wordle_api.ext import APIRouter
from . import models
from .constants import FACTORY, RANKER

router = APIRouter(tags=['Hint'])


@router.post("/", response_model=list[models.HintResult])
async def get_hints(query: models.HintQuery):
    corpus = FACTORY.get_corpus(query.corpus)
    filters = [WordFilter(x.letter, x.positions, x.exclude_positions, x.at_least, x.at_most) for x in query.query]
    words = corpus.get_potential_words(filters)
    results = RANKER.partition_score(words)

    if isinstance(query.limit, int):
        results = results.head(query.limit)

    return results.to_dict('records')


@router.get('/corpus', response_model=list[str])
async def get_corpus():
    return FACTORY.sources
