"""Cache em memória com validade (TTL) para consultas de leitura caras.

Guarda o resultado de consultas como a listagem paginada do catálogo, a
lista de gêneros e as estatísticas do dashboard. Toda escrita (cadastrar,
editar, remover filme ou adicionar avaliação) limpa o cache inteiro, então
quem gerencia o catálogo nunca enxerga um dado desatualizado.

Limitação conhecida: o cache vive na memória de UM processo. Com um único
worker do uvicorn (como neste projeto) isso é suficiente; com vários
workers, cada um teria o seu (e, para isso, o caminho seria Redis).
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from app.core.config import get_settings

_MISSING = object()


class TTLCache:
    def __init__(
        self,
        ttl_seconds: float = 60.0,
        max_items: int = 500,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._ttl = ttl_seconds
        self._max_items = max_items
        self._clock = clock
        self._store: dict[str, tuple[float, Any]] = {}

    def __len__(self) -> int:
        return len(self._store)

    def get(self, key: str, default: Any = None) -> Any:
        entry = self._store.get(key)
        if entry is None:
            return default
        expires_at, value = entry
        if self._clock() >= expires_at:
            del self._store[key]
            return default
        return value

    def set(self, key: str, value: Any) -> None:
        if len(self._store) >= self._max_items and key not in self._store:
            self._evict_one()
        self._store[key] = (self._clock() + self._ttl, value)

    def clear(self) -> None:
        self._store.clear()

    async def get_or_set(self, key: str, loader: Callable[[], Awaitable[Any]]) -> Any:
        """Devolve o valor em cache; se não houver (ou tiver expirado), chama
        `loader`, guarda o resultado e o devolve."""

        cached = self.get(key, _MISSING)
        if cached is not _MISSING:
            return cached
        value = await loader()
        self.set(key, value)
        return value

    def _evict_one(self) -> None:
        now = self._clock()
        for key, (expires_at, _) in self._store.items():
            if now >= expires_at:
                del self._store[key]
                return
        # nenhum expirado: remove o mais antigo (ordem de inserção)
        del self._store[next(iter(self._store))]


# TTL <= 0 desliga o cache na prática (tudo já nasce expirado).
query_cache = TTLCache(ttl_seconds=get_settings().cache_ttl_seconds)
