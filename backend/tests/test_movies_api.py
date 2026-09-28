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

TEST_ADMIN_EMAIL = "admin@teste.com"
TEST_ADMIN_SENHA = "senha-teste-123"


@pytest.fixture
async def client():
    """Cliente HTTP autenticado contra a app FastAPI, com SQLite em memória isolado."""

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
            session,
            nome="Admin Teste",
            email=TEST_ADMIN_EMAIL,
            senha_hash=hash_password(TEST_ADMIN_SENHA),
        )

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        login_response = await ac.post(
            "/api/v1/auth/login", json={"email": TEST_ADMIN_EMAIL, "senha": TEST_ADMIN_SENHA}
        )
        assert login_response.status_code == 200, login_response.text
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


MOVIE_PAYLOAD = {
    "titulo": "Duna",
    "diretor": "Denis Villeneuve",
    "ano_lancamento": 2021,
    "generos": ["Ficção Científica", "Aventura"],
    "sinopse": "Um jovem herdeiro precisa proteger sua família e seu povo.",
    "duracao_minutos": 155,
    "url_poster": None,
    "url_backdrop": None,
}


async def test_full_movie_and_review_flow(client: httpx.AsyncClient) -> None:
    # cadastro (exige login — o client da fixture já está autenticado)
    create_response = await client.post("/api/v1/movies", json=MOVIE_PAYLOAD)
    assert create_response.status_code == 201
    movie = create_response.json()
    assert movie["titulo"] == "Duna"
    assert movie["diretor"] == "Denis Villeneuve"
    assert set(movie["generos"]) == {"Ficção Científica", "Aventura"}
    movie_id = movie["sk_movie_id"]

    # aparece no catálogo paginado
    catalog_response = await client.get("/api/v1/movies", params={"page": 1, "size": 10})
    assert catalog_response.status_code == 200
    assert catalog_response.json()["total"] == 1

    # busca por título (case-insensitive)
    search_response = await client.get("/api/v1/movies", params={"q": "duna"})
    assert search_response.json()["total"] == 1

    # filtro por gênero inexistente não retorna nada
    filtered_response = await client.get("/api/v1/movies", params={"genero": "Terror"})
    assert filtered_response.json()["total"] == 0

    # avaliação na escala de 0 a 10 (endpoint público, não exige login)
    review_response = await client.post(
        f"/api/v1/movies/{movie_id}/reviews",
        json={"nome": "Ana", "nota": 8.5, "comentario": "Ótimo filme!"},
    )
    assert review_response.status_code == 201
    review = review_response.json()
    assert review["nota"] == 8.5

    # detalhe reflete média e contagem de avaliações
    detail_response = await client.get(f"/api/v1/movies/{movie_id}")
    detail = detail_response.json()
    assert detail["qtd_avaliacoes"] == 1
    assert detail["nota_media"] == 8.5
    assert len(detail["reviews"]) == 1

    # atualização
    update_payload = {**MOVIE_PAYLOAD, "titulo": "Duna: Parte Um"}
    update_response = await client.put(f"/api/v1/movies/{movie_id}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["titulo"] == "Duna: Parte Um"

    # remoção
    delete_response = await client.delete(f"/api/v1/movies/{movie_id}")
    assert delete_response.status_code == 204

    empty_catalog_response = await client.get("/api/v1/movies")
    assert empty_catalog_response.json()["total"] == 0


async def test_get_unknown_movie_returns_404(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/movies/nao-existe")
    assert response.status_code == 404


async def test_create_movie_requires_at_least_one_genre(client: httpx.AsyncClient) -> None:
    payload = {**MOVIE_PAYLOAD, "generos": []}
    response = await client.post("/api/v1/movies", json=payload)
    assert response.status_code == 422
