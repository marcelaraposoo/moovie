import httpx
import pytest
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.auth import models as auth_models  # noqa: F401  Registra admin_users no metadata.
from app.auth.repository import create as create_admin
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.movies import models  # noqa: F401  Registra as tabelas no metadata.

ADMIN_EMAIL = "admin@teste.com"
ADMIN_SENHA = "senha-teste-123"


@pytest.fixture
async def anonymous_client():
    """Cliente HTTP SEM login, contra um banco com um administrador já cadastrado."""

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def override_get_db():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with test_session_factory() as session:
        await create_admin(session, nome="Admin Teste", email=ADMIN_EMAIL, senha_hash=hash_password(ADMIN_SENHA))

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


MOVIE_PAYLOAD = {
    "titulo": "Duna",
    "diretor": "Denis Villeneuve",
    "ano_lancamento": 2021,
    "generos": ["Ficção Científica"],
    "sinopse": "Sinopse de teste.",
    "duracao_minutos": 155,
    "url_poster": None,
    "url_backdrop": None,
}


async def test_login_com_credenciais_corretas(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.post(
        "/api/v1/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == ADMIN_EMAIL
    assert body["nome"] == "Admin Teste"
    # o cookie de sessão deve ter sido enviado
    assert "moovie_session" in response.cookies


async def test_login_com_senha_errada(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.post(
        "/api/v1/auth/login", json={"email": ADMIN_EMAIL, "senha": "senha-errada"}
    )
    assert response.status_code == 401


async def test_login_com_email_inexistente(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.post(
        "/api/v1/auth/login", json={"email": "ninguem@teste.com", "senha": ADMIN_SENHA}
    )
    assert response.status_code == 401


async def test_cadastrar_filme_sem_login_e_rejeitado(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.post("/api/v1/movies", json=MOVIE_PAYLOAD)
    assert response.status_code == 401


async def test_editar_filme_sem_login_e_rejeitado(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.put("/api/v1/movies/qualquer-id", json=MOVIE_PAYLOAD)
    assert response.status_code == 401


async def test_remover_filme_sem_login_e_rejeitado(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.delete("/api/v1/movies/qualquer-id")
    assert response.status_code == 401


async def test_catalogo_e_publico_sem_login(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.get("/api/v1/movies")
    assert response.status_code == 200


async def test_me_sem_login_e_rejeitado(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_login_e_depois_me_funciona(anonymous_client: httpx.AsyncClient) -> None:
    login_response = await anonymous_client.post(
        "/api/v1/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA}
    )
    assert login_response.status_code == 200

    me_response = await anonymous_client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["email"] == ADMIN_EMAIL


async def test_logout_invalida_a_sessao(anonymous_client: httpx.AsyncClient) -> None:
    await anonymous_client.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA})
    logout_response = await anonymous_client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 204

    me_response = await anonymous_client.get("/api/v1/auth/me")
    assert me_response.status_code == 401
