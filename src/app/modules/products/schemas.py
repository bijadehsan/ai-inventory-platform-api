from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

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
