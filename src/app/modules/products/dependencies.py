from typing import Annotated

from fastapi import Depends

from app.core.database import SessionDep
from app.modules.products.repository import ProductRepository
from app.modules.products.service import ProductService


def get_product_repository(session: SessionDep) -> ProductRepository:
    return ProductRepository(session)


ProductRepositoryDep = Annotated[ProductRepository, Depends(get_product_repository)]


def get_product_service(session: SessionDep, repository: ProductRepositoryDep) -> ProductService:
    return ProductService(session, repository)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
