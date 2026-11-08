from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import engine
from app.core.error_handlers import register_error_handlers
from app.modules.health.router import router as health_router
from app.modules.products.router import router as products_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(title="Inventory API", lifespan=lifespan)

register_error_handlers(app)

app.include_router(health_router)
app.include_router(products_router, prefix="/api/v1")
