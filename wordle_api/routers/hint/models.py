from pydantic import conint, constr, validator

from wordle_api.ext import CamelModel
from .constants import FACTORY

Letter = constr(regex=r'^[a-zA-Z]$', strip_whitespace=True)
Position = conint(ge=1, le=5)


class PositionFixed(CamelModel):
    letter: Letter
    position: Position


class PositionInclude(CamelModel):
    letter: Letter
    exclude_position: list[Position]


class HintQuery(CamelModel):
    fixed: list[PositionFixed]
    include: list[PositionInclude]
    exclude: list[Letter]
    corpus: str
    limit: conint(ge=1) = None

    @validator('*', whole=True)
    def validate_inputs(cls, inputs):
        return inputs

    @validator('corpus')
    def validate_corpus(cls, corpus: str):
        sources = FACTORY.sources
        if corpus not in sources:
            raise ValueError(f"Invalid corpus: {corpus}. Use one of {sources}]")
        return corpus


class HintResult(CamelModel):
    word: str
    score: int | float
