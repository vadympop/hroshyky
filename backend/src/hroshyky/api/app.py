"""FastAPI application factory."""

from typing import Literal

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

router = APIRouter(tags=["system"])


class Health(BaseModel):
    """Liveness answer."""

    status: Literal["ok"] = "ok"


@router.get("/health", summary="Liveness probe")
async def health() -> Health:
    """Answer as soon as the process is up. It does not touch the database."""
    return Health()


def create_app() -> FastAPI:
    """Build the application. It reads no settings, so the schema export needs no environment."""
    app = FastAPI(title="Hroshyky API", version="0.1.0")
    app.include_router(router)
    return app
