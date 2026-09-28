import { useEffect, useState } from "react";
import { extractErrorMessage, fetchDashboard } from "../api/client";
import type { DashboardStats } from "../types/movie";

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

  useEffect(() => {
    fetchDashboard()
      .then(setStats)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="loading-state">Carregando estatísticas...</p>;
  if (error) return <p className="form-error">{error}</p>;
  if (!stats) return null;

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
          <h2>Filmes por década</h2>
          <BarChart
            emptyText="Ainda não há filmes com ano de lançamento."
            rows={stats.filmes_por_decada.map((d) => ({
              label: `${d.decada}s`,
              value: d.quantidade,
            }))}
          />
        </div>
      </div>
    </section>
  );
}
