"""Camada de acesso a dados (repository) do domínio de filmes.

Só sabe conversar com o banco via SQLAlchemy — não decide regra de
negócio (isso é responsabilidade de app/movies/service.py). Mantém a
arquitetura em camadas: router -> service -> repository -> SQLAlchemy.
"""

from __future__ import annotations

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.movies.models import DimGenre, DimMovie, DimPerson, DimReview, MovieReview

DIRETOR = "Diretor"


def _movie_query():
    return select(DimMovie).options(
        selectinload(DimMovie.genres),
        selectinload(DimMovie.people),
        selectinload(DimMovie.reviews_summary),
        selectinload(DimMovie.reviews),
    )


async def get_or_create_genre(db: AsyncSession, nome: str) -> DimGenre:
    result = await db.execute(select(DimGenre).where(DimGenre.nome_genero == nome))
    genre = result.scalar_one_or_none()
    if genre is None:
        genre = DimGenre(nome_genero=nome)
        db.add(genre)
        await db.flush()
    return genre


async def get_or_create_director(db: AsyncSession, nome: str) -> DimPerson:
    result = await db.execute(
        select(DimPerson).where(DimPerson.nome_pessoa == nome, DimPerson.tipo_pessoa == DIRETOR)
    )
    person = result.scalar_one_or_none()
    if person is None:
        person = DimPerson(nome_pessoa=nome, tipo_pessoa=DIRETOR)
        db.add(person)
        await db.flush()
    return person


async def find_by_id(db: AsyncSession, sk_movie_id: str) -> DimMovie | None:
    stmt = _movie_query().where(DimMovie.sk_movie_id == sk_movie_id)
    return (await db.execute(stmt)).unique().scalar_one_or_none()


async def find_page(
    db: AsyncSession,
    *,
    page: int,
    size: int,
    q: str | None,
    genero: str | None,
) -> tuple[list[DimMovie], int]:
    stmt = _movie_query()
    count_stmt = select(func.count(func.distinct(DimMovie.sk_movie_id))).select_from(DimMovie)

    if genero:
        stmt = stmt.join(DimMovie.genres).where(DimGenre.nome_genero == genero)
        count_stmt = count_stmt.join(DimMovie.genres).where(DimGenre.nome_genero == genero)

    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(DimMovie.titulo.ilike(like))
        count_stmt = count_stmt.where(DimMovie.titulo.ilike(like))

    total = (await db.execute(count_stmt)).scalar_one()

    # Títulos que começam com letra vêm primeiro; números/símbolos por último.
    starts_with_letter = case((DimMovie.titulo.op("GLOB")("[A-Za-z]*"), 0), else_=1)
    stmt = (
        stmt.order_by(starts_with_letter, func.lower(DimMovie.titulo))
        .offset((page - 1) * size)
        .limit(size)
    )
    movies = (await db.execute(stmt)).unique().scalars().all()

    return list(movies), total


async def list_genre_names(db: AsyncSession) -> list[str]:
    result = await db.execute(select(DimGenre.nome_genero).order_by(DimGenre.nome_genero))
    return [row[0] for row in result.all()]


async def save(db: AsyncSession, movie: DimMovie) -> None:
    db.add(movie)
    await db.commit()


async def delete(db: AsyncSession, movie: DimMovie) -> None:
    await db.delete(movie)
    await db.commit()


async def add_review_row(
    db: AsyncSession, movie: DimMovie, *, nome: str, nota: float, comentario: str
) -> MovieReview:
    review = MovieReview(sk_movie_id=movie.sk_movie_id, nome=nome, nota=nota, comentario=comentario)
    db.add(review)

    summary = movie.reviews_summary
    if summary is None:
        summary = DimReview(sk_movie_id=movie.sk_movie_id, qtd_avaliacoes_usuarios=0)
        db.add(summary)

    total_pontos = (summary.nota_media_usuarios or 0.0) * summary.qtd_avaliacoes_usuarios
    summary.qtd_avaliacoes_usuarios += 1
    summary.nota_media_usuarios = (total_pontos + nota) / summary.qtd_avaliacoes_usuarios

    await db.commit()
    await db.refresh(review)
    return review
