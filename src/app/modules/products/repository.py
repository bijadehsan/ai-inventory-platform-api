from collections.abc import Sequence

from sqlalchemy import ColumnElement, Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import SortOrder
from app.modules.products.models import Product
from app.modules.products.schemas import ProductListParams, ProductSortField

SORT_COLUMNS = {
    ProductSortField.NAME: Product.name,
    ProductSortField.SKU: Product.sku,
    ProductSortField.UNIT_PRICE: Product.unit_price,
    ProductSortField.CREATED_AT: Product.created_at,
}


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _filters(params: ProductListParams) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = []
    if params.search:
        pattern = f"%{_escape_like(params.search.strip())}%"
        conditions.append(
            or_(Product.name.ilike(pattern, escape="\\"), Product.sku.ilike(pattern, escape="\\"))
        )
    if params.is_active is not None:
        conditions.append(Product.is_active.is_(params.is_active))
    if params.min_price is not None:
        conditions.append(Product.unit_price >= params.min_price)
    if params.max_price is not None:
        conditions.append(Product.unit_price <= params.max_price)
    return conditions


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, product_id: int) -> Product | None:
        return await self._session.get(Product, product_id)

    async def get_by_sku(self, sku: str) -> Product | None:
        return await self._session.scalar(select(Product).where(Product.sku == sku))

    async def search(self, params: ProductListParams) -> tuple[Sequence[Product], int]:
        """Return one page of matching products and the total number of matches."""
        filtered: Select[Product] = select(Product).where(*_filters(params))

        total = await self._session.scalar(
            select(func.count()).select_from(filtered.order_by(None).subquery())
        )

        sort_column = SORT_COLUMNS[params.sort_by]
        direction = sort_column.asc() if params.sort_order is SortOrder.ASC else sort_column.desc()
        page = await self._session.scalars(
            filtered.order_by(direction, Product.id.asc()).offset(params.offset).limit(params.limit)
        )
        return page.all(), total or 0

    def add(self, product: Product) -> None:
        self._session.add(product)
