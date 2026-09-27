"""Regras de negócio de autenticação (camada service)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import repository
from app.auth.models import AdminUser
from app.core.security import create_session_token, verify_password


class InvalidCredentialsError(Exception):
    """Credenciais de login inválidas."""


async def authenticate(db: AsyncSession, *, email: str, senha: str) -> tuple[AdminUser, str]:
    """Verifica e-mail/senha e retorna (usuário, token de sessão)."""

    admin = await repository.get_by_email(db, email)
    if admin is None or not verify_password(senha, admin.senha_hash):
        raise InvalidCredentialsError("E-mail ou senha inválidos")

    token = create_session_token(admin.id)
    return admin, token
