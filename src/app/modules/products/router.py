from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.pagination import Page
from app.modules.products.dependencies import ProductServiceDep
from app.modules.products.schemas import (
    ProductCreate,
    ProductListParams,
    ProductRead,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, service: ProductServiceDep) -> ProductRead:
    product = await service.create(data)
    return ProductRead.model_validate(product)


@router.get("")
async def list_products(
    params: Annotated[ProductListParams, Query()], service: ProductServiceDep
) -> Page[ProductRead]:
    products, total = await service.search(params)
    return Page(
        items=[ProductRead.model_validate(product) for product in products],
        total=total,
        offset=params.offset,
        limit=params.limit,
    )


@router.get("/{product_id}")
async def get_product(product_id: int, service: ProductServiceDep) -> ProductRead:
    product = await service.get(product_id)
    return ProductRead.model_validate(product)


@router.patch("/{product_id}")
async def update_product(
    product_id: int, data: ProductUpdate, service: ProductServiceDep
) -> ProductRead:
    product = await service.update(product_id, data)
    return ProductRead.model_validate(product)
