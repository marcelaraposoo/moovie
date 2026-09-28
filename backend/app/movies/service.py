"""Regras de negócio (camada service) do domínio de filmes.

Orquestra o repository: get-or-create de gênero/diretor, geração do id de
negócio, preservação de elenco ao editar, atualização do resumo de
avaliações, e o mapeamento de DimMovie -> dict que os schemas Pydantic
consomem.
"""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.movies import repository
from app.movies.models import DimMovie, DimReview, MovieReview
from app.movies.repository import DIRETOR
from app.movies.schemas import MovieCreate, MovieUpdate, ReviewCreate


def _next_id_filme() -> str:
    """Gera um identificador de negócio simples para filmes cadastrados manualmente.

    Os filmes importados via CSV já trazem `id_filme` (ex: um id do TMDB);
    para os cadastrados pela aplicação, geramos um identificador próprio.
    """

    return f"mv-{uuid4().hex[:10]}"


def _director_name(movie: DimMovie) -> str | None:
    for person in movie.people:
        if person.tipo_pessoa == DIRETOR:
            return person.nome_pessoa
    return None


def to_list_item(movie: DimMovie) -> dict:
    return {
        "sk_movie_id": movie.sk_movie_id,
        "id_filme": movie.id_filme,
        "titulo": movie.titulo,
        "ano_lancamento": movie.ano_lancamento,
        "sinopse": movie.sinopse,
        "url_poster": movie.url_poster,
        "url_backdrop": movie.url_backdrop,
        "generos": [g.nome_genero for g in movie.genres],
        "diretor": _director_name(movie),
        "nota_media": (
            movie.reviews_summary.nota_media_usuarios if movie.reviews_summary else None
        ),
        "qtd_avaliacoes": (
            movie.reviews_summary.qtd_avaliacoes_usuarios if movie.reviews_summary else 0
        ),
    }


def to_detail(movie: DimMovie) -> dict:
    data = to_list_item(movie)
    data["duracao_minutos"] = movie.duracao_minutos
    data["reviews"] = list(reversed(movie.reviews))  # mais recentes primeiro
    return data


async def list_movies(
    db: AsyncSession, *, page: int, size: int, q: str | None, genero: str | None
) -> tuple[list[dict], int]:
    movies, total = await repository.find_page(db, page=page, size=size, q=q, genero=genero)
    return [to_list_item(m) for m in movies], total


async def get_movie(db: AsyncSession, sk_movie_id: str) -> DimMovie | None:
    return await repository.find_by_id(db, sk_movie_id)


async def list_genres(db: AsyncSession) -> list[str]:
    return await repository.list_genre_names(db)


async def create_movie(db: AsyncSession, payload: MovieCreate) -> DimMovie:
    movie = DimMovie(
        id_filme=_next_id_filme(),
        titulo=payload.titulo,
        ano_lancamento=payload.ano_lancamento,
        duracao_minutos=payload.duracao_minutos,
        sinopse=payload.sinopse,
        url_poster=payload.url_poster,
        url_backdrop=payload.url_backdrop,
    )

    director = await repository.get_or_create_director(db, payload.diretor)
    movie.people = [director]
    movie.genres = [await repository.get_or_create_genre(db, nome) for nome in payload.generos]
    movie.reviews_summary = DimReview(qtd_avaliacoes_usuarios=0, nota_media_usuarios=None)

    await repository.save(db, movie)
    return await repository.find_by_id(db, movie.sk_movie_id)  # type: ignore[return-value]


async def update_movie(db: AsyncSession, movie: DimMovie, payload: MovieUpdate) -> DimMovie:
    movie.titulo = payload.titulo
    movie.ano_lancamento = payload.ano_lancamento
    movie.duracao_minutos = payload.duracao_minutos
    movie.sinopse = payload.sinopse
    movie.url_poster = payload.url_poster
    movie.url_backdrop = payload.url_backdrop

    director = await repository.get_or_create_director(db, payload.diretor)
    # preserva outras pessoas (ex: atores importados via CSV) e só substitui o diretor
    movie.people = [p for p in movie.people if p.tipo_pessoa != DIRETOR] + [director]
    movie.genres = [await repository.get_or_create_genre(db, nome) for nome in payload.generos]

    await repository.save(db, movie)
    return await repository.find_by_id(db, movie.sk_movie_id)  # type: ignore[return-value]


async def delete_movie(db: AsyncSession, movie: DimMovie) -> None:
    await repository.delete(db, movie)


async def add_review(db: AsyncSession, movie: DimMovie, payload: ReviewCreate) -> MovieReview:
    return await repository.add_review_row(
        db,
        movie,
        nome=payload.nome.strip(),
        nota=payload.nota,
        comentario=payload.comentario.strip(),
    )
