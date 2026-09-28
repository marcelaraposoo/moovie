from __future__ import annotations

from pydantic import BaseModel


class GenreCount(BaseModel):
    genero: str
    quantidade: int


class DecadeCount(BaseModel):
    decada: int
    quantidade: int


class DashboardStats(BaseModel):
    total_filmes: int
    total_avaliacoes: int
    nota_media_geral: float | None
    generos_mais_comuns: list[GenreCount]
    filmes_por_decada: list[DecadeCount]
