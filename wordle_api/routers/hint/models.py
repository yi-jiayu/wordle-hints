from pydantic import conint, constr, validator

from wordle_api.ext import CamelModel
from .constants import FACTORY, WORD_LENGTH

Letter = constr(regex=r'^[a-zA-Z]$', strip_whitespace=True)
Position = conint(ge=1, le=WORD_LENGTH)


class LetterDesc(CamelModel):
    letter: Letter
    positions: list[conint(ge=1)]
    exclude_positions: list[conint(ge=1)]
    at_least: conint(ge=0, le=WORD_LENGTH)
    at_most: conint(ge=0, le=WORD_LENGTH)


class HintQuery(CamelModel):
    query: list[LetterDesc]
    corpus: str
    limit: conint(ge=1) = None

    @validator('corpus')
    def validate_corpus(cls, corpus: str):
        sources = FACTORY.sources
        if corpus not in sources:
            raise ValueError(f"Invalid corpus: {corpus}. Use one of {sources}]")
        return corpus


class HintResult(CamelModel):
    word: str
    partition: int
    frequency: int
