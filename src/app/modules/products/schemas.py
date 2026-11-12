from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.core.pagination import SortOrder

Sku = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Price = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]


class ProductCreate(BaseModel):
    sku: Sku
    name: Name
    description: str | None = None
    unit_price: Price


class ProductUpdate(BaseModel):
    name: Name | None = None
    description: str | None = None
    unit_price: Price | None = None
    is_active: bool | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    description: str | None
    unit_price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductSortField(StrEnum):
    NAME = "name"
    SKU = "sku"
    UNIT_PRICE = "unit_price"
    CREATED_AT = "created_at"


class ProductListParams(BaseModel):
    """Query parameters for GET /products (filters, sorting, pagination)."""

    model_config = ConfigDict(extra="forbid")

    search: Annotated[str | None, Field(max_length=100)] = None
    is_active: bool | None = None
    min_price: Annotated[Decimal | None, Field(ge=0)] = None
    max_price: Annotated[Decimal | None, Field(ge=0)] = None
    sort_by: ProductSortField = ProductSortField.CREATED_AT
    sort_order: SortOrder = SortOrder.DESC
    offset: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=100)] = 20

    @model_validator(mode="after")
    def check_price_range(self) -> Self:
        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise ValueError("min_price must be less than or equal to max_price")
        return self
