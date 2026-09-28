"""Modelo do Administrador (usuário único que gerencia o catálogo)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utc_now() -> datetime:
    return datetime.now(UTC)


class AdminUser(Base):
    """Conta do Administrador. O sistema é single-user por natureza (ver PDF
    da atividade: "o usuário será o Administrador"), mas a tabela suporta
    mais de um registro caso, no futuro, mais de um administrador precise
    gerenciar o catálogo.
    """

    __tablename__ = "admin_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
