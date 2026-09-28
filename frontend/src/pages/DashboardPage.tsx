import { useEffect, useState } from "react";
import { extractErrorMessage, fetchDashboard } from "../api/client";
import type { DashboardStats } from "../types/movie";

type Granularidade = "ano" | "decada";

// acima disso, o gráfico por ano fica ilegível: mostramos só os mais recentes
const MAX_ANOS = 30;

interface BarRow {
  label: string;
  value: number;
}

function BarChart({ rows, emptyText }: { rows: BarRow[]; emptyText: string }) {
  if (rows.length === 0) {
    return <p className="empty-state">{emptyText}</p>;
  }

  const max = Math.max(...rows.map((row) => row.value), 1);

  return (
    <ul className="bar-chart">
      {rows.map((row) => (
        <li key={row.label} className="bar-row">
          <span className="bar-label">{row.label}</span>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${(row.value / max) * 100}%` }} />
          </div>
          <span className="bar-value">{row.value.toLocaleString("pt-BR")}</span>
        </li>
      ))}
    </ul>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [granularidade, setGranularidade] = useState<Granularidade>("ano");

  useEffect(() => {
    fetchDashboard()
      .then(setStats)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="loading-state">Carregando estatísticas...</p>;
  if (error) return <p className="form-error">{error}</p>;
  if (!stats) return null;

  const anosVisiveis = stats.filmes_por_ano.slice(-MAX_ANOS);
  const anosOcultos = stats.filmes_por_ano.length - anosVisiveis.length;
  const rowsPorPeriodo: BarRow[] =
    granularidade === "ano"
      ? anosVisiveis.map((a) => ({ label: String(a.ano), value: a.quantidade }))
      : stats.filmes_por_decada.map((d) => ({ label: `${d.decada}s`, value: d.quantidade }));

  return (
    <section className="dashboard-page">
      <h1 className="dashboard-title">Dashboard</h1>
      <p className="dashboard-subtitle">Visão geral do catálogo.</p>

      <div className="stat-cards">
        <div className="stat-card">
          <span className="stat-card-value">{stats.total_filmes.toLocaleString("pt-BR")}</span>
          <span className="stat-card-label">filmes no catálogo</span>
        </div>
        <div className="stat-card">
          <span className="stat-card-value">{stats.total_avaliacoes.toLocaleString("pt-BR")}</span>
          <span className="stat-card-label">avaliações registradas</span>
        </div>
        <div className="stat-card">
          <span className="stat-card-value">
            {stats.nota_media_geral !== null ? stats.nota_media_geral.toFixed(1) : "—"}
          </span>
          <span className="stat-card-label">nota média geral (0 a 10)</span>
        </div>
      </div>

      <div className="dashboard-panels">
        <div className="dashboard-panel">
          <h2>Gêneros mais comuns</h2>
          <BarChart
            emptyText="Ainda não há gêneros cadastrados."
            rows={stats.generos_mais_comuns.map((g) => ({ label: g.genero, value: g.quantidade }))}
          />
        </div>

        <div className="dashboard-panel">
          <div className="dashboard-panel-header">
            <h2>{granularidade === "ano" ? "Filmes por ano" : "Filmes por década"}</h2>
            <div className="segmented" role="group" aria-label="Agrupar filmes por">
              <button
                type="button"
                className={`segmented-option ${granularidade === "ano" ? "segmented-option-active" : ""}`}
                aria-pressed={granularidade === "ano"}
                onClick={() => setGranularidade("ano")}
              >
                Ano
              </button>
              <button
                type="button"
                className={`segmented-option ${granularidade === "decada" ? "segmented-option-active" : ""}`}
                aria-pressed={granularidade === "decada"}
                onClick={() => setGranularidade("decada")}
              >
                Década
              </button>
            </div>
          </div>
          <BarChart emptyText="Ainda não há filmes com ano de lançamento." rows={rowsPorPeriodo} />
          {granularidade === "ano" && anosOcultos > 0 && (
            <p className="dashboard-note">Mostrando os {MAX_ANOS} anos mais recentes.</p>
          )}
        </div>
      </div>
    </section>
  );
}
