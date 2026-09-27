import { useState } from "react";
import type { FormEvent } from "react";
import RatingControl from "./RatingControl";

interface ReviewFormProps {
  onSubmit: (data: { nome: string; nota: number; comentario: string }) => Promise<void>;
}

export default function ReviewForm({ onSubmit }: ReviewFormProps) {
  const [nome, setNome] = useState("");
  const [nota, setNota] = useState(5);
  const [comentario, setComentario] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (!nome.trim() || !comentario.trim()) {
      setError("Preencha seu nome, uma nota de 0 a 10 e escreva um comentário.");
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit({ nome: nome.trim(), nota, comentario: comentario.trim() });
      setNome("");
      setNota(5);
      setComentario("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível enviar sua avaliação.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="review-form" onSubmit={handleSubmit}>
      <h3>Deixe sua avaliação</h3>

      {error && <p className="form-error">{error}</p>}

      <label className="field">
        <span>Seu nome</span>
        <input
          className="input"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          maxLength={120}
          required
        />
      </label>

      <label className="field">
        <span>Sua nota (0 a 10)</span>
        <RatingControl value={nota} onChange={setNota} />
      </label>

      <label className="field">
        <span>Sua resenha</span>
        <textarea
          className="input"
          value={comentario}
          onChange={(e) => setComentario(e.target.value)}
          maxLength={4000}
          rows={4}
          required
        />
      </label>

      <button type="submit" className="btn btn-primary" disabled={submitting}>
        {submitting ? "Enviando..." : "Enviar avaliação"}
      </button>
    </form>
  );
}
