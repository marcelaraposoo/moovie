import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { addReview, deleteMovie, extractErrorMessage, fetchMovie } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import RatingBadge from "../components/RatingBadge";
import ReviewForm from "../components/ReviewForm";
import ReviewList from "../components/ReviewList";
import type { MovieDetail } from "../types/movie";

export default function MovieDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [movie, setMovie] = useState<MovieDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  function loadMovie() {
    if (!id) return;
    setLoading(true);
    setError(null);
    fetchMovie(id)
      .then(setMovie)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }

  useEffect(loadMovie, [id]);

  async function handleAddReview(data: { nome: string; nota: number; comentario: string }) {
    if (!id) return;
    await addReview(id, data);
    loadMovie();
  }

  async function handleDelete() {
    if (!id || !movie) return;
    const confirmado = window.confirm(`Remover "${movie.titulo}" do catálogo? Essa ação não pode ser desfeita.`);
    if (!confirmado) return;

    try {
      await deleteMovie(id);
      navigate("/");
    } catch (err) {
      alert(extractErrorMessage(err));
    }
  }

  if (loading) return <p className="loading-state">Carregando...</p>;
  if (error) return <p className="form-error">{error}</p>;
  if (!movie) return null;

  const backdrop = movie.url_backdrop ?? movie.url_poster;

  return (
    <article className="movie-page">
      <div
        className="movie-backdrop"
        style={
          backdrop
            ? {
                backgroundImage: `linear-gradient(180deg, rgba(16,23,26,0.25) 0%, rgba(16,23,26,0.98) 100%), url(${backdrop})`,
              }
            : undefined
        }
      >
        <button type="button" className="back-link" onClick={() => navigate(-1)}>
          ← Voltar
        </button>
      </div>

      <div className="movie-hero-row">
        {movie.url_poster ? (
          <img src={movie.url_poster} alt="" className="movie-poster-large" />
        ) : (
          <div className="movie-poster-large poster-card-fallback">
            <span>{movie.titulo}</span>
          </div>
        )}

        <div className="movie-hero-info">
          <h1 className="movie-title">{movie.titulo}</h1>
          <p className="movie-meta-line">
            {movie.ano_lancamento ?? "—"}
            {movie.duracao_minutos ? ` · ${movie.duracao_minutos} min` : ""} · dirigido por{" "}
            <strong>{movie.diretor ?? "desconhecido"}</strong>
          </p>

          <div className="genre-tags">
            {movie.generos.map((genero) => (
              <span key={genero} className="genre-tag">
                {genero}
              </span>
            ))}
          </div>

          <div className="movie-rating-row">
            {movie.qtd_avaliacoes > 0 ? (
              <>
                <RatingBadge value={movie.nota_media ?? 0} size="lg" />
                <span className="movie-rating-count">
                  média de {movie.qtd_avaliacoes} {movie.qtd_avaliacoes === 1 ? "avaliação" : "avaliações"}
                </span>
              </>
            ) : (
              <span className="movie-rating-count">Ainda sem avaliações</span>
            )}
          </div>

          {isAuthenticated && (
            <div className="movie-actions">
              <Link to={`/filmes/${movie.sk_movie_id}/editar`} className="btn btn-secondary">
                Editar filme
              </Link>
              <button type="button" className="btn btn-danger" onClick={handleDelete}>
                Remover filme
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="movie-body">
        <section className="movie-synopsis-section">
          <h2>Sinopse</h2>
          <p className="movie-synopsis">{movie.sinopse || "Sem sinopse cadastrada."}</p>
        </section>

        <section className="movie-reviews-section">
          <h2>Avaliações</h2>
          <ReviewList reviews={movie.reviews} />
          <ReviewForm onSubmit={handleAddReview} />
        </section>
      </div>
    </article>
  );
}
