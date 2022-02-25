from pydantic import BaseModel


def camelCase(field: str):
    x, *items = field.split('_')
    return ''.join([x.lower(), *[y.title() for y in items]])


class CamelModel(BaseModel):
    class Config:
        alias_generator = camelCase
        allow_population_by_field_name = True
