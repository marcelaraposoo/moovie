import httpx

MOVIE_A = {
    "titulo": "Duna",
    "diretor": "Denis Villeneuve",
    "ano_lancamento": 2021,
    "generos": ["Ficção Científica"],
    "sinopse": "Sinopse A.",
    "duracao_minutos": 155,
    "url_poster": None,
    "url_backdrop": None,
}

MOVIE_B = {
    "titulo": "Matrix",
    "diretor": "Lana Wachowski",
    "ano_lancamento": 1999,
    "generos": ["Ficção Científica", "Ação"],
    "sinopse": "Sinopse B.",
    "duracao_minutos": 136,
    "url_poster": None,
    "url_backdrop": None,
}


async def test_dashboard_sem_login_e_rejeitado(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.get("/api/v1/dashboard")
    assert response.status_code == 401


async def test_dashboard_com_dados(client: httpx.AsyncClient) -> None:
    movie_a = (await client.post("/api/v1/movies", json=MOVIE_A)).json()
    await client.post("/api/v1/movies", json=MOVIE_B)

    await client.post(
        f"/api/v1/movies/{movie_a['sk_movie_id']}/reviews",
        json={"nome": "Ana", "nota": 8.0, "comentario": "Muito bom"},
    )
    await client.post(
        f"/api/v1/movies/{movie_a['sk_movie_id']}/reviews",
        json={"nome": "Bia", "nota": 6.0, "comentario": "Ok"},
    )

    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200
    body = response.json()

    assert body["total_filmes"] == 2
    assert body["total_avaliacoes"] == 2
    assert body["nota_media_geral"] == 7.0

    generos = {g["genero"]: g["quantidade"] for g in body["generos_mais_comuns"]}
    assert generos["Ficção Científica"] == 2
    assert generos["Ação"] == 1

    decadas = {d["decada"]: d["quantidade"] for d in body["filmes_por_decada"]}
    assert decadas[2020] == 1
    assert decadas[1990] == 1


async def test_dashboard_sem_nenhum_filme(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["total_filmes"] == 0
    assert body["total_avaliacoes"] == 0
    assert body["nota_media_geral"] is None
    assert body["generos_mais_comuns"] == []
    assert body["filmes_por_decada"] == []
