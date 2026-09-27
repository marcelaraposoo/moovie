interface PaginationProps {
  page: number;
  pages: number;
  onChange: (page: number) => void;
}

export default function Pagination({ page, pages, onChange }: PaginationProps) {
  if (pages <= 1) return null;

  return (
    <nav className="pagination" aria-label="Paginação do catálogo">
      <button
        type="button"
        className="btn btn-secondary btn-sm"
        disabled={page <= 1}
        onClick={() => onChange(page - 1)}
      >
        ← Anterior
      </button>
      <span className="pagination-info">
        Página {page} de {pages}
      </span>
      <button
        type="button"
        className="btn btn-secondary btn-sm"
        disabled={page >= pages}
        onClick={() => onChange(page + 1)}
      >
        Próxima →
      </button>
    </nav>
  );
}
