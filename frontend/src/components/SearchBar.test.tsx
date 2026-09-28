import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import SearchBar from "./SearchBar";

describe("SearchBar", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("lista os gêneros recebidos, incluindo a opção 'Todos'", () => {
    render(
      <SearchBar
        q=""
        genero=""
        genres={["Drama", "Comédia"]}
        onSearch={vi.fn()}
        onGenreChange={vi.fn()}
      />
    );
    expect(screen.getByText("Todos os gêneros")).toBeInTheDocument();
    expect(screen.getByText("Drama")).toBeInTheDocument();
    expect(screen.getByText("Comédia")).toBeInTheDocument();
  });

  it("só chama onSearch depois do debounce (350ms) parar de digitar", () => {
    const onSearch = vi.fn();
    render(
      <SearchBar q="" genero="" genres={[]} onSearch={onSearch} onGenreChange={vi.fn()} />
    );

    const input = screen.getByLabelText("Buscar filme");
    fireEvent.change(input, { target: { value: "duna" } });

    // ainda não deve ter chamado — o debounce não terminou
    expect(onSearch).not.toHaveBeenCalled();

    vi.advanceTimersByTime(350);
    expect(onSearch).toHaveBeenCalledWith("duna");
  });

  it("chama onGenreChange imediatamente ao trocar o select (sem debounce)", () => {
    const onGenreChange = vi.fn();
    render(
      <SearchBar
        q=""
        genero=""
        genres={["Terror"]}
        onSearch={vi.fn()}
        onGenreChange={onGenreChange}
      />
    );

    fireEvent.change(screen.getByLabelText("Filtrar por gênero"), {
      target: { value: "Terror" },
    });
    expect(onGenreChange).toHaveBeenCalledWith("Terror");
  });

  it("resincroniza o campo de busca quando 'q' muda de fora (ex: botão voltar)", () => {
    const { rerender } = render(
      <SearchBar q="duna" genero="" genres={[]} onSearch={vi.fn()} onGenreChange={vi.fn()} />
    );
    const input = screen.getByLabelText("Buscar filme") as HTMLInputElement;
    expect(input.value).toBe("duna");

    rerender(
      <SearchBar q="matrix" genero="" genres={[]} onSearch={vi.fn()} onGenreChange={vi.fn()} />
    );
    expect(input.value).toBe("matrix");
  });
});
