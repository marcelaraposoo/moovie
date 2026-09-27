import { useEffect, useState } from "react";

interface SearchBarProps {
  q: string;
  genero: string;
  genres: string[];
  onSearch: (q: string) => void;
  onGenreChange: (genero: string) => void;
}

export default function SearchBar({ q, genero, genres, onSearch, onGenreChange }: SearchBarProps) {
  const [term, setTerm] = useState(q);

  // resincroniza se o "q" mudar de fora (ex: botão voltar do navegador)
  useEffect(() => {
    setTerm(q);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  // debounce simples: espera o usuário parar de digitar antes de buscar
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (term !== q) onSearch(term);
    }, 350);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [term]);

  return (
    <div className="search-bar">
      <input
        type="search"
        placeholder="Buscar filme pelo título..."
        value={term}
        onChange={(e) => setTerm(e.target.value)}
        className="input search-input"
        aria-label="Buscar filme"
      />
      <select
        value={genero}
        onChange={(e) => onGenreChange(e.target.value)}
        className="input genre-select"
        aria-label="Filtrar por gênero"
      >
        <option value="">Todos os gêneros</option>
        {genres.map((g) => (
          <option key={g} value={g}>
            {g}
          </option>
        ))}
      </select>
    </div>
  );
}
