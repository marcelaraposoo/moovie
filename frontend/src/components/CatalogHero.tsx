import { Link } from "react-router-dom";
import type { MovieListItem } from "../types/movie";

interface CatalogHeroProps {
  movie: MovieListItem | null;
  totalFilmes: number;
}

export default function CatalogHero({ movie, totalFilmes }: CatalogHeroProps) {
  return (
    <section className="hero">
      <div className="hero-copy">
        <span className="hero-tag">{movie ? "Em destaque" : "Seu catálogo"}</span>

        {movie ? (
          <>
            <h1 className="hero-title">{movie.titulo}</h1>
            <p className="hero-subtitle">
              {movie.ano_lancamento ?? "—"} · dirigido por {movie.diretor ?? "desconhecido"}
              {movie.qtd_avaliacoes > 0 ? ` · nota ${movie.nota_media?.toFixed(1)}/10` : ""}
            </p>
            <Link to={`/filmes/${movie.sk_movie_id}`} className="btn btn-primary">
              Ver detalhes
            </Link>
          </>
        ) : (
          <>
            <h1 className="hero-title">Nenhum filme cadastrado ainda</h1>
            <p className="hero-subtitle">Comece adicionando o primeiro filme ao seu catálogo.</p>
            <Link to="/filmes/novo" className="btn btn-primary">
              Adicionar filme
            </Link>
          </>
        )}
      </div>

      {movie?.url_poster && (
        <div className="hero-poster-frame">
          <img src={movie.url_poster} alt="" className="hero-poster-img" />
        </div>
      )}

      <div className="hero-stat">
        <span className="hero-stat-value">{totalFilmes}</span>
        <span className="hero-stat-label">{totalFilmes === 1 ? "filme catalogado" : "filmes catalogados"}</span>
      </div>
    </section>
  );
}
