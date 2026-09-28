"""Fixtures compartilhadas entre todos os arquivos de teste."""

from __future__ import annotations

import httpx
import pytest
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.auth import models as auth_models  # noqa: F401  Registra admin_users no metadata.
from app.auth.repository import create as create_admin
from app.core.cache import query_cache
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.movies import models  # noqa: F401  Registra as tabelas no metadata.

ADMIN_EMAIL = "admin@teste.com"
ADMIN_SENHA = "senha-teste-123"


@pytest.fixture
async def anonymous_client():
    """Cliente HTTP SEM login, contra um banco em memória com 1 admin já cadastrado."""

    # o cache é global do processo: sem limpar, o resultado guardado por um
    # teste (com outro banco em memória) vazaria para o teste seguinte.
    query_cache.clear()

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def override_get_db():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with test_session_factory() as session:
        await create_admin(
            session, nome="Admin Teste", email=ADMIN_EMAIL, senha_hash=hash_password(ADMIN_SENHA)
        )

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    query_cache.clear()
    await engine.dispose()


@pytest.fixture
async def client(anonymous_client: httpx.AsyncClient) -> httpx.AsyncClient:
    """O mesmo cliente acima, mas já autenticado como o Administrador de teste."""

    login_response = await anonymous_client.post(
        "/api/v1/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA}
    )
    assert login_response.status_code == 200, login_response.text
    return anonymous_client
