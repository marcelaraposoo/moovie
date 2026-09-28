from app.db.base import Base
from app.movies import models  # noqa: F401  Registra os modelos ORM.


def test_movie_schema_registers_expected_tables() -> None:
    """As 10 tabelas do schema estrela original devem continuar intactas.

    Usamos "é subconjunto de" (<=), não "é igual a" (==), de propósito: o
    módulo de autenticação (bônus) registra a tabela adicional
    `admin_users` no mesmo Base.metadata, e isso é esperado — o que este
    teste garante é que o schema *fornecido pela atividade* não foi alterado
    ou perdido, não que nada mais possa ser adicionado por cima dele.
    """

    expected_tables = {
        "bridge_movie_company",
        "bridge_movie_genre",
        "bridge_movie_person",
        "dim_companies",
        "dim_genres",
        "dim_movies",
        "dim_people",
        "dim_reviews",
        "fact_movies_performance",
        "movie_reviews",
    }

    assert expected_tables <= set(Base.metadata.tables)
    assert "idioma_original" not in Base.metadata.tables["dim_movies"].columns


def test_movie_review_columns_match_shared_csv() -> None:
    table = Base.metadata.tables["movie_reviews"]

    assert {"sk_movie_review_id", "sk_movie_id", "nome", "nota", "comentario"} <= set(
        table.columns.keys()
    )
    assert table.primary_key.columns.keys() == ["sk_movie_review_id"]
