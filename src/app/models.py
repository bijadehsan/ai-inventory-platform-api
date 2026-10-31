"""Import every ORM model here so Alembic autogenerate can see all tables."""

from app.core.database import Base
from app.modules.products.models import Product

__all__ = ["Base", "Product"]
