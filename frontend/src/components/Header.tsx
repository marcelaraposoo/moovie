import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import CowLogo from "./CowLogo";

export default function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, admin, logout } = useAuth();
  const isCatalog = location.pathname === "/";

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  return (
    <header className="site-header">
      <div className="site-header-inner">
        <Link to="/" className="brand">
          <CowLogo />
          <span className="brand-word">
            Moo<span className="brand-accent">vie</span>
          </span>
        </Link>

        <nav className="site-nav">
          <Link to="/" className={`nav-link ${isCatalog ? "nav-link-active" : ""}`}>
            Catálogo
          </Link>
          {isAuthenticated && (
            <Link to="/filmes/novo" className="btn btn-primary btn-sm">
              Adicionar filme
            </Link>
          )}
        </nav>

        {isAuthenticated ? (
          <div className="admin-badge">
            <span className="admin-avatar" aria-hidden="true">
              {admin?.nome.charAt(0).toUpperCase() ?? "A"}
            </span>
            <span className="admin-name">{admin?.nome}</span>
            <button type="button" className="btn btn-secondary btn-sm" onClick={handleLogout}>
              Sair
            </button>
          </div>
        ) : (
          <Link to="/login" className="btn btn-secondary btn-sm">
            Entrar
          </Link>
        )}
      </div>
    </header>
  );
}
