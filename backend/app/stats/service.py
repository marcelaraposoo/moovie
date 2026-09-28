from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import query_cache
from app.stats import repository
from app.stats.schemas import DashboardStats, DecadeCount, GenreCount, YearCount


async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    return await query_cache.get_or_set("stats:dashboard", lambda: _compute_stats(db))


async def _compute_stats(db: AsyncSession) -> DashboardStats:
    total_filmes = await repository.count_movies(db)
    total_avaliacoes = await repository.count_reviews(db)
    nota_media_geral = await repository.average_rating(db)
    generos = await repository.top_genres(db)
    anos = await repository.movies_by_year(db)
    decadas = await repository.movies_by_decade(db)

    return DashboardStats(
        total_filmes=total_filmes,
        total_avaliacoes=total_avaliacoes,
        nota_media_geral=round(nota_media_geral, 2) if nota_media_geral is not None else None,
        generos_mais_comuns=[GenreCount(genero=g, quantidade=q) for g, q in generos],
        filmes_por_ano=[YearCount(ano=a, quantidade=q) for a, q in anos],
        filmes_por_decada=[DecadeCount(decada=d, quantidade=q) for d, q in decadas],
    )
