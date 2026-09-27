"""Dependências FastAPI para proteger rotas administrativas."""

from __future__ import annotations

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import repository
from app.auth.models import AdminUser
from app.core.security import verify_session_token
from app.db.session import get_db

COOKIE_NAME = "moovie_session"


async def get_current_admin(
    moovie_session: str | None = Cookie(default=None, alias=COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    """Exige uma sessão válida; usado para proteger criar/editar/remover filmes."""

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Faça login para gerenciar o catálogo",
    )

    if not moovie_session:
        raise unauthorized

    admin_id = verify_session_token(moovie_session)
    if admin_id is None:
        raise unauthorized

    admin = await repository.get_by_id(db, admin_id)
    if admin is None:
        raise unauthorized

    return admin
