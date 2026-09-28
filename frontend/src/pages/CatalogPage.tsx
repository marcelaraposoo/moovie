import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { deleteMovie, extractErrorMessage, fetchGenres, fetchMovies } from "../api/client";
import CatalogHero from "../components/CatalogHero";
import MovieCard from "../components/MovieCard";
import Pagination from "../components/Pagination";
import SearchBar from "../components/SearchBar";
import type { MovieListItem } from "../types/movie";

const PAGE_SIZE = 18;

export default function CatalogPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const q = searchParams.get("q") ?? "";
  const genero = searchParams.get("genero") ?? "";
  const page = Number(searchParams.get("page") ?? "1") || 1;

  const [movies, setMovies] = useState<MovieListItem[]>([]);
  const [genres, setGenres] = useState<string[]>([]);
  const [featured, setFeatured] = useState<MovieListItem | null>(null);
  const [pages, setPages] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGenres().then(setGenres).catch(() => setGenres([]));

    // amostra independente dos filtros, só para escolher um "destaque" estável
    fetchMovies({ page: 1, size: 24 })
      .then((data) => {
        const best = [...data.items].sort((a, b) => (b.nota_media ?? -1) - (a.nota_media ?? -1))[0];
        setFeatured(best ?? null);
      })
      .catch(() => setFeatured(null));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchMovies({ page, size: PAGE_SIZE, q: q || undefined, genero: genero || undefined })
      .then((data) => {
        if (cancelled) return;
        setMovies(data.items);
        setPages(data.pages);
        setTotal(data.total);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(extractErrorMessage(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [page, q, genero]);

  function updateParams(next: { q?: string; genero?: string; page?: number }) {
    const params = new URLSearchParams(searchParams);
    if (next.q !== undefined) {
      if (next.q) params.set("q", next.q);
      else params.delete("q");
    }
    if (next.genero !== undefined) {
      if (next.genero) params.set("genero", next.genero);
      else params.delete("genero");
    }
    if (next.page !== undefined) {
      if (next.page > 1) params.set("page", String(next.page));
      else params.delete("page");
    }
    setSearchParams(params);
  }

  function handleSearch(term: string) {
    updateParams({ q: term, page: 1 });
  }

  function handleGenreChange(value: string) {
    updateParams({ genero: value, page: 1 });
  }

  function handlePageChange(nextPage: number) {
    updateParams({ page: nextPage });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleDelete(movie: MovieListItem) {
    const confirmado = window.confirm(`Remover "${movie.titulo}" do catálogo? Essa ação não pode ser desfeita.`);
    if (!confirmado) return;

    try {
      await deleteMovie(movie.sk_movie_id);
      setMovies((current) => current.filter((m) => m.sk_movie_id !== movie.sk_movie_id));
      setTotal((t) => t - 1);
    } catch (err) {
      alert(extractErrorMessage(err));
    }
  }

  return (
    <>
      <CatalogHero movie={featured} totalFilmes={total} />

      <section className="catalog-section">
        <SearchBar
          q={q}
          genero={genero}
          genres={genres}
          onSearch={handleSearch}
          onGenreChange={handleGenreChange}
        />

        {error && <p className="form-error">{error}</p>}
        {loading && <p className="loading-state">Carregando filmes...</p>}

        {!loading && movies.length === 0 && !error && (
          <p className="empty-state">Nenhum filme encontrado com esses filtros.</p>
        )}

        <div className="poster-grid">
          {movies.map((movie) => (
            <MovieCard key={movie.sk_movie_id} movie={movie} onDelete={handleDelete} />
          ))}
        </div>

        <Pagination page={page} pages={pages} onChange={handlePageChange} />
      </section>
    </>
  );
}
