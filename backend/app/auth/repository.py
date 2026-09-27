"""Acesso a dados do Administrador (camada repository)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import AdminUser


async def get_by_email(db: AsyncSession, email: str) -> AdminUser | None:
    result = await db.execute(select(AdminUser).where(AdminUser.email == email.lower().strip()))
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, admin_id: str) -> AdminUser | None:
    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, *, nome: str, email: str, senha_hash: str) -> AdminUser:
    admin = AdminUser(nome=nome, email=email.lower().strip(), senha_hash=senha_hash)
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin


async def count(db: AsyncSession) -> int:
    from sqlalchemy import func

    result = await db.execute(select(func.count()).select_from(AdminUser))
    return result.scalar_one()
