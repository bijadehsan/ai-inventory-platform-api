import os

# Must run before any app import: settings are read once and cached.
os.environ["POSTGRES_DB"] = "inventory_test"

import asyncio  # noqa: E402
from collections.abc import AsyncIterator  # noqa: E402

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # noqa: E402
from sqlalchemy.pool import NullPool  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.database import get_session  # noqa: E402
from app.main import app  # noqa: E402

TEST_DATABASE = "inventory_test"


async def _create_test_database() -> None:
    admin_url = get_settings().database_url.set(database="postgres")
    engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    async with engine.connect() as connection:
        exists = await connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": TEST_DATABASE}
        )
        if not exists:
            await connection.execute(text(f'CREATE DATABASE "{TEST_DATABASE}"'))
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def test_database() -> None:
    """Create the test database once and bring it to the latest migration."""
    assert get_settings().postgres_db == TEST_DATABASE, "refusing to run tests on a non-test DB"
    asyncio.run(_create_test_database())
    command.upgrade(Config(toml_file="pyproject.toml"), "head")


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """A session inside a transaction that is always rolled back: every test starts clean."""
    engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
