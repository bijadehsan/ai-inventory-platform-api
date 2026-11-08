from collections.abc import Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, session: AsyncSession, repository: ProductRepository) -> None:
        self._session = session
        self._repository = repository

    async def create(self, data: ProductCreate) -> Product:
        if await self._repository.get_by_sku(data.sku) is not None:
            raise ConflictError(f"A product with SKU '{data.sku}' already exists.")

        product = Product(**data.model_dump())
        self._repository.add(product)
        await self._commit_or_conflict(f"A product with SKU '{data.sku}' already exists.")
        await self._session.refresh(product)
        return product

    async def get(self, product_id: int) -> Product:
        product = await self._repository.get(product_id)
        if product is None:
            raise NotFoundError(f"Product {product_id} was not found.")
        return product

    async def get_page(self, *, offset: int, limit: int) -> Sequence[Product]:
        return await self._repository.get_page(offset=offset, limit=limit)

    async def update(self, product_id: int, data: ProductUpdate) -> Product:
        product = await self.get(product_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self._session.commit()
        await self._session.refresh(product)
        return product

    async def _commit_or_conflict(self, message: str) -> None:
        try:
            await self._session.commit()
        except IntegrityError as error:
            await self._session.rollback()
            raise ConflictError(message) from error
