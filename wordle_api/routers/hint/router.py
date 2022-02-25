from wordle_api.ext import APIRouter
from . import models
from .constants import FACTORY

router = APIRouter(tags=['Hint'])


@router.post("/", response_model=list[models.HintResult])
async def get_hints(query: models.HintQuery):
    corpus = FACTORY.get_corpus(query.corpus)
    fixed_letters = {x.position: x.letter for x in query.fixed} or None
    include = [x.letter for x in query.include if x.letter]
    exclude = [x for x in query.exclude if x] + [(x.letter, x.exclude_position) for x in query.include]

    words = corpus.get_potential_words(fixed_letters, include, exclude).rename(columns=str.lower)
    if isinstance(query.limit, int):
        words = words.head(query.limit)

    return words.to_dict(orient='records')


@router.get('/corpus', response_model=list[str])
async def get_corpus():
    return FACTORY.sources
