import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { fetchDashboard } from "../api/client";
import type { DashboardStats } from "../types/movie";
import DashboardPage from "./DashboardPage";

vi.mock("../api/client", () => ({
  fetchDashboard: vi.fn().mockResolvedValue({
    total_filmes: 100,
    total_avaliacoes: 20,
    nota_media_geral: 7.5,
    generos_mais_comuns: [{ genero: "Drama", quantidade: 60 }],
    filmes_por_ano: [
      { ano: 2016, quantidade: 10 },
      { ano: 2021, quantidade: 30 },
    ],
    filmes_por_decada: [
      { decada: 2010, quantidade: 40 },
      { decada: 2020, quantidade: 60 },
    ],
  }),
  extractErrorMessage: vi.fn(() => "erro"),
}));

describe("DashboardPage", () => {
  it("mostra os filmes por ano por padrão", async () => {
    render(<DashboardPage />);

    expect(await screen.findByText("Filmes por ano")).toBeInTheDocument();
    expect(screen.getByText("2016")).toBeInTheDocument();
    expect(screen.getByText("2021")).toBeInTheDocument();
    expect(screen.queryByText("2010s")).not.toBeInTheDocument();
  });

  it("troca para década ao clicar em 'Década' e volta para ano", async () => {
    render(<DashboardPage />);
    await screen.findByText("Filmes por ano");

    fireEvent.click(screen.getByRole("button", { name: "Década" }));
    expect(screen.getByText("Filmes por década")).toBeInTheDocument();
    expect(screen.getByText("2010s")).toBeInTheDocument();
    expect(screen.queryByText("2016")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Ano" }));
    expect(screen.getByText("Filmes por ano")).toBeInTheDocument();
    expect(screen.getByText("2016")).toBeInTheDocument();
  });

  it("mostra só os 30 anos mais recentes quando há mais que isso", async () => {
    const muitosAnos: DashboardStats = {
      total_filmes: 35,
      total_avaliacoes: 0,
      nota_media_geral: null,
      generos_mais_comuns: [],
      filmes_por_ano: Array.from({ length: 35 }, (_, i) => ({ ano: 1990 + i, quantidade: 1 })),
      filmes_por_decada: [],
    };
    vi.mocked(fetchDashboard).mockResolvedValueOnce(muitosAnos);

    render(<DashboardPage />);

    expect(await screen.findByText("Mostrando os 30 anos mais recentes.")).toBeInTheDocument();
    expect(screen.queryByText("1990")).not.toBeInTheDocument();
    expect(screen.getByText("2024")).toBeInTheDocument();
  });
});
