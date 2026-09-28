"""Consultas agregadas para o dashboard (camada repository)."""

from __future__ import annotations

from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.movies.models import DimGenre, DimMovie, MovieReview, bridge_movie_genre


async def count_movies(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(DimMovie))
    return result.scalar_one()


async def count_reviews(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(MovieReview))
    return result.scalar_one()


async def average_rating(db: AsyncSession) -> float | None:
    result = await db.execute(select(func.avg(MovieReview.nota)))
    return result.scalar_one()


async def top_genres(db: AsyncSession, *, limit: int = 8) -> list[tuple[str, int]]:
    stmt = (
        select(DimGenre.nome_genero, func.count(bridge_movie_genre.c.sk_movie_id))
        .select_from(bridge_movie_genre)
        .join(DimGenre, DimGenre.sk_genre_id == bridge_movie_genre.c.sk_genre_id)
        .group_by(DimGenre.nome_genero)
        .order_by(func.count(bridge_movie_genre.c.sk_movie_id).desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return [(nome, qtd) for nome, qtd in result.all()]


async def movies_by_year(db: AsyncSession) -> list[tuple[int, int]]:
    stmt = (
        select(DimMovie.ano_lancamento, func.count())
        .where(DimMovie.ano_lancamento.isnot(None))
        .group_by(DimMovie.ano_lancamento)
        .order_by(DimMovie.ano_lancamento)
    )
    result = await db.execute(stmt)
    return [(int(ano), qtd) for ano, qtd in result.all()]


async def movies_by_decade(db: AsyncSession) -> list[tuple[int, int]]:
    # cast para inteiro: o SQLAlchemy 2 faz `/` como divisão decimal, então
    # sem o CAST 2021 viraria 2021.0 (e não 2020) ao multiplicar por 10.
    decada = cast(DimMovie.ano_lancamento / 10, Integer) * 10
    stmt = (
        select(decada.label("decada"), func.count())
        .where(DimMovie.ano_lancamento.isnot(None))
        .group_by(decada)
        .order_by(decada)
    )
    result = await db.execute(stmt)
    return [(int(dec), qtd) for dec, qtd in result.all()]
