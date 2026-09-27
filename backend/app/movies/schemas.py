"""Schemas Pydantic usados pela API de filmes e avaliações."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Avaliações (reviews)
# ---------------------------------------------------------------------------
class ReviewCreate(BaseModel):
    """Payload para registrar uma nova avaliação de um filme.

    A nota é lançada diretamente na escala de 0 a 10 (mesma escala do
    banco, ver CheckConstraint em MovieReview), conforme confirmado pelo
    professor.
    """

    nome: str = Field(..., min_length=1, max_length=120, description="Nome de quem avaliou")
    nota: float = Field(..., ge=0, le=10, description="Nota de 0 a 10")
    comentario: str = Field(..., min_length=1, max_length=4000)


class ReviewOut(BaseModel):
    sk_movie_review_id: str
    nome: str
    comentario: str
    created_at: datetime
    nota: float

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Filmes
# ---------------------------------------------------------------------------
class MovieBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=500)
    diretor: str = Field(..., min_length=1, max_length=255)
    ano_lancamento: int = Field(..., ge=1888, le=2100)
    generos: list[str] = Field(..., min_length=1, description="Um ou mais gêneros do filme")
    sinopse: str | None = Field(default=None, max_length=4000)
    duracao_minutos: int | None = Field(default=None, ge=1, le=1000)
    url_poster: str | None = Field(default=None, max_length=2048)
    url_backdrop: str | None = Field(default=None, max_length=2048)

    @field_validator("generos")
    @classmethod
    def _limpa_generos(cls, value: list[str]) -> list[str]:
        limpos = [g.strip() for g in value if g and g.strip()]
        if not limpos:
            raise ValueError("informe ao menos um gênero")
        # remove duplicados preservando a ordem
        vistos: set[str] = set()
        unicos = []
        for genero in limpos:
            chave = genero.lower()
            if chave not in vistos:
                vistos.add(chave)
                unicos.append(genero)
        return unicos

    @field_validator("titulo", "diretor")
    @classmethod
    def _limpa_texto(cls, value: str) -> str:
        return value.strip()


class MovieCreate(MovieBase):
    pass


class MovieUpdate(MovieBase):
    pass


class MovieListItem(BaseModel):
    sk_movie_id: str
    id_filme: str
    titulo: str
    ano_lancamento: int | None
    sinopse: str | None
    url_poster: str | None
    url_backdrop: str | None
    generos: list[str]
    diretor: str | None
    nota_media: float | None = Field(default=None, description="Média das notas, escala 0-10")
    qtd_avaliacoes: int

    model_config = {"from_attributes": True}


class MovieDetail(MovieListItem):
    duracao_minutos: int | None
    reviews: list[ReviewOut]


class Page(BaseModel):
    items: list[MovieListItem]
    total: int
    page: int
    size: int
    pages: int
