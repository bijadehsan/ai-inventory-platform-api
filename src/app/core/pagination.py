from enum import StrEnum

from pydantic import BaseModel


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class Page[T](BaseModel):
    items: list[T]
    total: int
    offset: int
    limit: int
