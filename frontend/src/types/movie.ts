export interface Review {
  sk_movie_review_id: string;
  nome: string;
  comentario: string;
  created_at: string;
  nota: number; // escala 0-10
}

export interface MovieListItem {
  sk_movie_id: string;
  id_filme: string;
  titulo: string;
  ano_lancamento: number | null;
  sinopse: string | null;
  url_poster: string | null;
  url_backdrop: string | null;
  generos: string[];
  diretor: string | null;
  nota_media: number | null; // escala 0-10
  qtd_avaliacoes: number;
}

export interface MovieDetail extends MovieListItem {
  duracao_minutos: number | null;
  reviews: Review[];
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface MovieFormData {
  titulo: string;
  diretor: string;
  ano_lancamento: number;
  generos: string[];
  sinopse: string;
  duracao_minutos: number | null;
  url_poster: string | null;
  url_backdrop: string | null;
}

export interface ReviewFormData {
  nome: string;
  nota: number; // escala 0-10
  comentario: string;
}
