"""Rotas de autenticação: login, logout e sessão atual."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service
from app.auth.dependencies import COOKIE_NAME, get_current_admin
from app.auth.models import AdminUser
from app.auth.schemas import AdminOut, LoginRequest
from app.core.config import get_settings
from app.db.session import get_db

router = APIRouter()


@router.post("/login", response_model=AdminOut, summary="Autentica o Administrador")
async def login(
    payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
) -> AdminOut:
    settings = get_settings()
    try:
        admin, token = await service.authenticate(db, email=payload.email, senha=payload.senha)
    except service.InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=60 * 60 * 12,
        path="/",
    )
    return AdminOut.model_validate(admin)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Encerra a sessão")
async def logout(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me", response_model=AdminOut, summary="Retorna o Administrador logado")
async def me(admin: AdminUser = Depends(get_current_admin)) -> AdminOut:
    return AdminOut.model_validate(admin)
