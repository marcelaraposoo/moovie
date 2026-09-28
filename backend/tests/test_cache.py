import httpx

from app.core.cache import TTLCache


class FakeClock:
    """Relógio controlável, para testar expiração sem `sleep`."""

    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_guarda_e_devolve_o_valor() -> None:
    cache = TTLCache(ttl_seconds=60, clock=FakeClock())
    cache.set("chave", {"a": 1})
    assert cache.get("chave") == {"a": 1}


def test_chave_inexistente_devolve_o_padrao() -> None:
    cache = TTLCache(ttl_seconds=60, clock=FakeClock())
    assert cache.get("nao-existe") is None
    assert cache.get("nao-existe", "padrao") == "padrao"


def test_valor_expira_depois_do_ttl() -> None:
    clock = FakeClock()
    cache = TTLCache(ttl_seconds=60, clock=clock)
    cache.set("chave", "valor")

    clock.now += 59
    assert cache.get("chave") == "valor"

    clock.now += 2
    assert cache.get("chave") is None
    assert len(cache) == 0


def test_ttl_zero_desliga_o_cache() -> None:
    cache = TTLCache(ttl_seconds=0, clock=FakeClock())
    cache.set("chave", "valor")
    assert cache.get("chave") is None


def test_clear_remove_tudo() -> None:
    cache = TTLCache(ttl_seconds=60, clock=FakeClock())
    cache.set("a", 1)
    cache.set("b", 2)
    cache.clear()
    assert len(cache) == 0


def test_limite_de_itens_remove_o_mais_antigo() -> None:
    cache = TTLCache(ttl_seconds=60, max_items=2, clock=FakeClock())
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)

    assert len(cache) == 2
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3


async def test_get_or_set_so_chama_o_loader_uma_vez() -> None:
    cache = TTLCache(ttl_seconds=60, clock=FakeClock())
    chamadas = 0

    async def loader() -> str:
        nonlocal chamadas
        chamadas += 1
        return "resultado"

    assert await cache.get_or_set("k", loader) == "resultado"
    assert await cache.get_or_set("k", loader) == "resultado"
    assert chamadas == 1


async def test_get_or_set_recarrega_depois_de_expirar() -> None:
    clock = FakeClock()
    cache = TTLCache(ttl_seconds=10, clock=clock)
    chamadas = 0

    async def loader() -> int:
        nonlocal chamadas
        chamadas += 1
        return chamadas

    assert await cache.get_or_set("k", loader) == 1
    clock.now += 11
    assert await cache.get_or_set("k", loader) == 2


# --- integração: o cache precisa ser invalidado quando os dados mudam ---

MOVIE = {
    "titulo": "Duna",
    "diretor": "Denis Villeneuve",
    "ano_lancamento": 2021,
    "generos": ["Ficção Científica"],
    "sinopse": "Sinopse.",
    "duracao_minutos": 155,
    "url_poster": None,
    "url_backdrop": None,
}


async def test_catalogo_em_cache_e_atualizado_ao_cadastrar_e_remover(
    client: httpx.AsyncClient,
) -> None:
    assert (await client.get("/api/v1/movies")).json()["total"] == 0  # entra no cache

    created = (await client.post("/api/v1/movies", json=MOVIE)).json()
    assert (await client.get("/api/v1/movies")).json()["total"] == 1

    await client.delete(f"/api/v1/movies/{created['sk_movie_id']}")
    assert (await client.get("/api/v1/movies")).json()["total"] == 0


async def test_nota_media_no_catalogo_atualiza_apos_nova_avaliacao(
    client: httpx.AsyncClient,
) -> None:
    created = (await client.post("/api/v1/movies", json=MOVIE)).json()

    antes = (await client.get("/api/v1/movies")).json()["items"][0]
    assert antes["qtd_avaliacoes"] == 0

    await client.post(
        f"/api/v1/movies/{created['sk_movie_id']}/reviews",
        json={"nome": "Ana", "nota": 9.0, "comentario": "Ótimo"},
    )

    depois = (await client.get("/api/v1/movies")).json()["items"][0]
    assert depois["qtd_avaliacoes"] == 1
    assert depois["nota_media"] == 9.0


async def test_lista_de_generos_atualiza_ao_cadastrar_filme_com_genero_novo(
    client: httpx.AsyncClient,
) -> None:
    assert (await client.get("/api/v1/genres")).json() == []  # entra no cache

    await client.post("/api/v1/movies", json=MOVIE)
    assert (await client.get("/api/v1/genres")).json() == ["Ficção Científica"]


async def test_dashboard_em_cache_e_atualizado_ao_cadastrar_filme(
    client: httpx.AsyncClient,
) -> None:
    assert (await client.get("/api/v1/dashboard")).json()["total_filmes"] == 0  # entra no cache

    await client.post("/api/v1/movies", json=MOVIE)
    assert (await client.get("/api/v1/dashboard")).json()["total_filmes"] == 1
