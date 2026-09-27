import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import type { MovieListItem } from "../types/movie";

interface MovieCardProps {
  movie: MovieListItem;
  onDelete: (movie: MovieListItem) => void;
}

export default function MovieCard({ movie, onDelete }: MovieCardProps) {
  const { isAuthenticated } = useAuth();

  return (
    <article className="poster-card">
      <Link to={`/filmes/${movie.sk_movie_id}`} className="poster-card-link" aria-label={movie.titulo}>
        {movie.url_poster ? (
          <img src={movie.url_poster} alt="" className="poster-card-img" loading="lazy" />
        ) : (
          <div className="poster-card-img poster-card-fallback">
            <span>{movie.titulo}</span>
          </div>
        )}

        {movie.qtd_avaliacoes > 0 && (
          <span className="poster-score" aria-label={`Nota ${movie.nota_media?.toFixed(1)} de 10`}>
            {movie.nota_media?.toFixed(1)}
          </span>
        )}
      </Link>

      {isAuthenticated && (
        <div className="poster-card-actions">
          <Link
            to={`/filmes/${movie.sk_movie_id}/editar`}
            className="icon-btn"
            title="Editar filme"
            aria-label="Editar filme"
          >
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 20h9" strokeLinecap="round" />
              <path
                d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </Link>
          <button
            type="button"
            className="icon-btn icon-btn-danger"
            title="Remover filme"
            aria-label="Remover filme"
            onClick={() => onDelete(movie)}
          >
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18" strokeLinecap="round" />
              <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
            </svg>
          </button>
        </div>
      )}
    </article>
  );
}
