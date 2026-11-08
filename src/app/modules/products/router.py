from typing import Annotated

from fastapi import APIRouter, Query, status

from app.modules.products.dependencies import ProductServiceDep
from app.modules.products.schemas import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, service: ProductServiceDep) -> ProductRead:
    product = await service.create(data)
    return ProductRead.model_validate(product)


@router.get("")
async def list_products(
    service: ProductServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ProductRead]:
    products = await service.get_page(offset=offset, limit=limit)
    return [ProductRead.model_validate(product) for product in products]


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
