from fastapi import APIRouter, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness: the process is up. Never checks dependencies."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(session: SessionDep, response: Response) -> dict[str, str]:
    """Readiness: the app can serve traffic (database reachable)."""
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError, OSError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable", "database": "unreachable"}
    return {"status": "ok", "database": "ok"}
