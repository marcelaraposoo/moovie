"""Script de carga inicial (seed) a partir dos CSVs oficiais da atividade.

Como usar
---------
1. Rode as migrations primeiro:

       cd backend
       .venv/bin/alembic upgrade head

2. Copie os 9 CSVs fornecidos para `backend/seed_data/` (os dois arquivos
   zipados entregues na atividade), usando exatamente estes nomes — eles já
   vêm assim nos arquivos originais:

       dim_companies.csv
       dim_genres.csv
       dim_movies.csv
       dim_people.csv
       dim_reviews.csv
       bridge_movie_company.csv
       bridge_movie_genre.csv
       bridge_movie_person.csv
       fact_movies_performance.csv
       movies_reviews.csv

3. Rode, a partir da pasta `backend/`:

       .venv/bin/python -m scripts.seed

O script lê e insere em lotes (chunks), então lida bem com tabelas grandes
(ex: bridge_movie_person tem ~745 mil linhas). Cada lote é reportado no
terminal conforme é inserido.

Colunas com nomes diferentes
-----------------------------
Os CSVs oficiais da atividade já usam exatamente os mesmos nomes de coluna
do modelo em `app/movies/models.py`, então normalmente você não precisa
mexer em nada. Caso use outro arquivo com nomes diferentes, ajuste
COLUMN_MAPPING abaixo (chave = nome do arquivo CSV).
"""

from __future__ import annotations

import asyncio
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from sqlalchemy import Table, func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.session import engine
from app.movies import models

SEED_DIR = Path(__file__).resolve().parent.parent / "seed_data"
CHUNK_SIZE = 5000

# Ordem de carga: dimensões antes das tabelas-ponte, do fato e das
# avaliações, por causa das chaves estrangeiras.
LOAD_ORDER: list[tuple[str, Any]] = [
    ("dim_companies.csv", models.DimCompany),
    ("dim_genres.csv", models.DimGenre),
    ("dim_movies.csv", models.DimMovie),
    ("dim_people.csv", models.DimPerson),
    ("bridge_movie_company.csv", models.bridge_movie_company),
    ("bridge_movie_genre.csv", models.bridge_movie_genre),
    ("bridge_movie_person.csv", models.bridge_movie_person),
    ("fact_movies_performance.csv", models.FactMoviePerformance),
    ("dim_reviews.csv", models.DimReview),
    ("movies_reviews.csv", models.MovieReview),
]

# Preencha aqui caso alguma coluna do seu CSV tenha um nome diferente da
# coluna correspondente no banco. Chave = nome do arquivo CSV.
COLUMN_MAPPING: dict[str, dict[str, str]] = {}


def _as_table(entity: Any) -> Table:
    return entity.__table__ if hasattr(entity, "__table__") else entity


def _unwrap_redundant_quotes(text: str) -> str:
    """Remove uma camada redundante de aspas que envolve o campo inteiro.

    Alguns textos da base (ex: títulos de filme) vêm com o valor inteiro
    envolvido em aspas, resultado de um escape extra feito na fonte
    original dos dados — por exemplo, o texto chega como
    '"biography: ""stone cold"" steve austin's last match"' quando o título
    de verdade é 'biography: "stone cold" steve austin's last match'.
    Se o texto começa E termina com aspas, removemos essa camada externa e
    desfazemos o escape (`""` -> `"`). Apelidos entre aspas que fazem parte
    do título de verdade são preservados (ex: Satie's "Parade").
    """

    while len(text) >= 2 and text.startswith('"') and text.endswith('"'):
        unwrapped = text[1:-1].replace('""', '"')
        if unwrapped == text:
            break
        text = unwrapped
    return text


def _coerce(value: str | None, column: Any) -> Any:
    """Converte o texto do CSV para o tipo Python esperado pela coluna."""

    if value is None or value == "":
        return None
    try:
        py_type = column.type.python_type
    except NotImplementedError:
        return value

    try:
        if py_type is int:
            return int(float(value))
        if py_type is float:
            return float(value)
        if py_type is Decimal:
            return Decimal(value)
        if py_type is date:
            return date.fromisoformat(value)
        if py_type is str:
            return _unwrap_redundant_quotes(value)
        return value
    except (TypeError, ValueError, InvalidOperation):
        return value


_seen_unique_values: dict[tuple[str, str], set[str]] = {}


def _dedupe_unique_value(table_name: str, column_name: str, value: str) -> str:
    """Garante um valor único por tabela+coluna sem descartar a linha.

    Alguns campos de texto colidem só depois da limpeza de aspas
    (_unwrap_redundant_quotes) — ex: duas produtoras gravadas de forma
    ligeiramente diferente na base viram o mesmo nome depois de limpas.
    Em vez de descartar a linha (o que deixaria "pendurada" qualquer outra
    tabela que referencia a chave primária dela por chave estrangeira),
    acrescentamos um pequeno sufixo ao texto para desfazer a colisão,
    preservando a linha e seu id original intactos.
    """

    seen = _seen_unique_values.setdefault((table_name, column_name), set())
    original = value
    n = 2
    while value in seen:
        value = f"{original} ({n})"
        n += 1
    seen.add(value)
    return value


def _row_batches(csv_path: Path, mapping: dict[str, str], table: Table):
    valid_columns = {name: table.columns[name] for name in table.columns}
    unique_text_columns = [
        name
        for name, col in valid_columns.items()
        if col.unique and str(col.type).startswith("VARCHAR")
    ]

    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        batch: list[dict] = []
        for raw_row in reader:
            row = {}
            for key, value in raw_row.items():
                column_name = mapping.get(key, key)
                if column_name not in valid_columns:
                    continue
                row[column_name] = _coerce(value, valid_columns[column_name])

            for column_name in unique_text_columns:
                if isinstance(row.get(column_name), str):
                    row[column_name] = _dedupe_unique_value(
                        table.name, column_name, row[column_name]
                    )

            batch.append(row)
            if len(batch) >= CHUNK_SIZE:
                yield batch
                batch = []
        if batch:
            yield batch


async def _load_table(
    conn: AsyncConnection, table: Table, csv_path: Path, mapping: dict[str, str]
) -> int:
    # ON CONFLICT DO NOTHING: alguns campos de texto colidem só depois da
    # limpeza de aspas (_unwrap_redundant_quotes) — ex: duas produtoras que
    # eram grafadas de forma diferente na base viram o mesmo nome depois de
    # limpas. Em vez de travar a carga inteira por causa de uma linha
    # duplicada, simplesmente ignoramos a repetição e seguimos em frente.
    stmt = sqlite_insert(table).on_conflict_do_nothing()

    total = 0
    for batch in _row_batches(csv_path, mapping, table):
        await conn.execute(stmt, batch)
        total += len(batch)
        print(f"  ... {total} linha(s) processadas em '{table.name}'", end="\r")
    return total


async def _already_seeded(conn: AsyncConnection) -> bool:
    """True se já existir pelo menos um filme cadastrado no banco."""

    result = await conn.execute(select(func.count()).select_from(models.DimMovie.__table__))
    return (result.scalar_one() or 0) > 0


async def seed() -> None:
    if not SEED_DIR.exists():
        print(f"[seed] pasta não encontrada: {SEED_DIR}. Crie-a e coloque os CSVs lá dentro.")
        return

    async with engine.begin() as conn:
        if await _already_seeded(conn):
            print(
                "[seed] o banco já contém filmes cadastrados — não vou rodar de novo em cima\n"
                "[seed] dos dados existentes (isso causaria erros de valor duplicado).\n"
                "[seed] Para recarregar do zero: pare o backend, apague o arquivo rocketlab.db,\n"
                "[seed] rode 'alembic upgrade head' e então rode este script de novo."
            )
            return

        for filename, entity in LOAD_ORDER:
            csv_path = SEED_DIR / filename
            if not csv_path.exists():
                print(f"[seed] arquivo não encontrado, pulando: {filename}")
                continue

            table = _as_table(entity)
            mapping = COLUMN_MAPPING.get(filename, {})
            total = await _load_table(conn, table, csv_path, mapping)
            print(f"[seed] {filename}: {total} linha(s) processadas em '{table.name}'" + " " * 10)

    print("[seed] concluído.")


if __name__ == "__main__":
    asyncio.run(seed())
