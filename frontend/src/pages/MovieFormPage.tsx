import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { createMovie, extractErrorMessage, fetchMovie, updateMovie } from "../api/client";
import type { MovieFormData } from "../types/movie";

interface MovieFormPageProps {
  mode: "create" | "edit";
}

const EMPTY_FORM: MovieFormData = {
  titulo: "",
  diretor: "",
  ano_lancamento: new Date().getFullYear(),
  generos: [],
  sinopse: "",
  duracao_minutos: null,
  url_poster: "",
  url_backdrop: "",
};

export default function MovieFormPage({ mode }: MovieFormPageProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [form, setForm] = useState<MovieFormData>(EMPTY_FORM);
  const [generosTexto, setGenerosTexto] = useState("");
  const [loading, setLoading] = useState(mode === "edit");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (mode === "edit" && id) {
      fetchMovie(id)
        .then((movie) => {
          setForm({
            titulo: movie.titulo,
            diretor: movie.diretor ?? "",
            ano_lancamento: movie.ano_lancamento ?? new Date().getFullYear(),
            generos: movie.generos,
            sinopse: movie.sinopse ?? "",
            duracao_minutos: movie.duracao_minutos,
            url_poster: movie.url_poster ?? "",
            url_backdrop: movie.url_backdrop ?? "",
          });
          setGenerosTexto(movie.generos.join(", "));
        })
        .catch((err) => setError(extractErrorMessage(err)))
        .finally(() => setLoading(false));
    }
  }, [mode, id]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    const generos = generosTexto
      .split(",")
      .map((g) => g.trim())
      .filter(Boolean);

    if (generos.length === 0) {
      setError("Informe ao menos um gênero (separado por vírgula, se houver mais de um).");
      return;
    }

    const payload: MovieFormData = { ...form, generos };

    setSaving(true);
    try {
      if (mode === "create") {
        const created = await createMovie(payload);
        navigate(`/filmes/${created.sk_movie_id}`);
      } else if (id) {
        await updateMovie(id, payload);
        navigate(`/filmes/${id}`);
      }
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="loading-state">Carregando...</p>;

  return (
    <section className="movie-form-page">
      <Link to={mode === "edit" && id ? `/filmes/${id}` : "/"} className="back-link">
        ← Cancelar
      </Link>

      <h1>{mode === "create" ? "Cadastrar filme" : "Editar filme"}</h1>

      {error && <p className="form-error">{error}</p>}

      <form className="movie-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Título *</span>
          <input
            className="input"
            value={form.titulo}
            onChange={(e) => setForm((f) => ({ ...f, titulo: e.target.value }))}
            required
            maxLength={500}
          />
        </label>

        <label className="field">
          <span>Diretor *</span>
          <input
            className="input"
            value={form.diretor}
            onChange={(e) => setForm((f) => ({ ...f, diretor: e.target.value }))}
            required
            maxLength={255}
          />
        </label>

        <div className="field-row">
          <label className="field">
            <span>Ano de lançamento *</span>
            <input
              type="number"
              className="input"
              value={form.ano_lancamento}
              onChange={(e) => setForm((f) => ({ ...f, ano_lancamento: Number(e.target.value) }))}
              required
              min={1888}
              max={2100}
            />
          </label>

          <label className="field">
            <span>Duração (minutos)</span>
            <input
              type="number"
              className="input"
              value={form.duracao_minutos ?? ""}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  duracao_minutos: e.target.value ? Number(e.target.value) : null,
                }))
              }
              min={1}
            />
          </label>
        </div>

        <label className="field">
          <span>Gênero(s) * (separe por vírgula, ex: "Ficção Científica, Aventura")</span>
          <input
            className="input"
            value={generosTexto}
            onChange={(e) => setGenerosTexto(e.target.value)}
            required
          />
        </label>

        <div className="field-row">
          <label className="field">
            <span>URL do pôster (vertical)</span>
            <input
              className="input"
              value={form.url_poster ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, url_poster: e.target.value }))}
              placeholder="https://..."
            />
          </label>

          <label className="field">
            <span>URL do backdrop (imagem larga, opcional)</span>
            <input
              className="input"
              value={form.url_backdrop ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, url_backdrop: e.target.value }))}
              placeholder="https://..."
            />
          </label>
        </div>

        <label className="field">
          <span>Sinopse</span>
          <textarea
            className="input"
            rows={5}
            maxLength={4000}
            value={form.sinopse ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, sinopse: e.target.value }))}
          />
        </label>

        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? "Salvando..." : mode === "create" ? "Cadastrar filme" : "Salvar alterações"}
        </button>
      </form>
    </section>
  );
}
