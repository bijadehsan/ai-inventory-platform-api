from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, product_id: int) -> Product | None:
        return await self._session.get(Product, product_id)

    async def get_by_sku(self, sku: str) -> Product | None:
        return await self._session.scalar(select(Product).where(Product.sku == sku))

    async def get_page(self, *, offset: int, limit: int) -> Sequence[Product]:
        statement = select(Product).order_by(Product.id).offset(offset).limit(limit)
        result = await self._session.scalars(statement)
        return result.all()

    def add(self, product: Product) -> None:
        self._session.add(product)
