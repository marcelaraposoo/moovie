"""Rotas HTTP do domínio de filmes: catálogo, detalhes, CRUD e avaliações."""

from __future__ import annotations

import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_admin
from app.auth.models import AdminUser
from app.db.session import get_db
from app.movies import service
from app.movies.models import DimMovie
from app.movies.schemas import (
    MovieCreate,
    MovieDetail,
    MovieListItem,
    MovieUpdate,
    Page,
    ReviewCreate,
    ReviewOut,
)

router = APIRouter()
genres_router = APIRouter()


async def _get_movie_or_404(db: AsyncSession, sk_movie_id: str) -> DimMovie:
    movie = await service.get_movie(db, sk_movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado")
    return movie


@router.get("", response_model=Page, summary="Lista paginada do catálogo, com busca e filtro")
async def list_movies(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    q: str | None = Query(None, description="Busca por título (case-insensitive)"),
    genero: str | None = Query(None, description="Filtra por um gênero exato"),
    db: AsyncSession = Depends(get_db),
) -> Page:
    items, total = await service.list_movies(db, page=page, size=size, q=q, genero=genero)
    pages = math.ceil(total / size) if total else 0
    return Page(
        items=[MovieListItem.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{sk_movie_id}", response_model=MovieDetail, summary="Detalhes de um filme e suas avaliações")
async def get_movie(sk_movie_id: str, db: AsyncSession = Depends(get_db)) -> MovieDetail:
    movie = await _get_movie_or_404(db, sk_movie_id)
    return MovieDetail.model_validate(service.to_detail(movie))


@router.post(
    "",
    response_model=MovieDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um novo filme",
)
async def create_movie(
    payload: MovieCreate,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> MovieDetail:
    movie = await service.create_movie(db, payload)
    return MovieDetail.model_validate(service.to_detail(movie))


@router.put("/{sk_movie_id}", response_model=MovieDetail, summary="Atualiza um filme existente")
async def update_movie(
    sk_movie_id: str,
    payload: MovieUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> MovieDetail:
    movie = await _get_movie_or_404(db, sk_movie_id)
    movie = await service.update_movie(db, movie, payload)
    return MovieDetail.model_validate(service.to_detail(movie))


@router.delete(
    "/{sk_movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um filme (e suas avaliações, em cascata)",
)
async def delete_movie(
    sk_movie_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> None:
    movie = await _get_movie_or_404(db, sk_movie_id)
    await service.delete_movie(db, movie)


@router.post(
    "/{sk_movie_id}/reviews",
    response_model=ReviewOut,
    status_code=status.HTTP_201_CREATED,
    summary="Adiciona uma avaliação (nota de 0 a 10 + comentário) a um filme",
)
async def add_review(
    sk_movie_id: str, payload: ReviewCreate, db: AsyncSession = Depends(get_db)
) -> ReviewOut:
    movie = await _get_movie_or_404(db, sk_movie_id)
    review = await service.add_review(db, movie, payload)
    return ReviewOut.model_validate(review)


@genres_router.get("", response_model=list[str], summary="Lista os gêneros já cadastrados")
async def list_genres(db: AsyncSession = Depends(get_db)) -> list[str]:
    return await service.list_genres(db)
