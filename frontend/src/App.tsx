import { Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import ProtectedRoute from "./auth/ProtectedRoute";
import Header from "./components/Header";
import CatalogPage from "./pages/CatalogPage";
import LoginPage from "./pages/LoginPage";
import MovieDetailPage from "./pages/MovieDetailPage";
import MovieFormPage from "./pages/MovieFormPage";
import "./styles.css";

export default function App() {
  return (
    <AuthProvider>
      <div className="app">
        <div className="film-strip" aria-hidden="true" />
        <Header />

        <main className="app-main">
          <Routes>
            <Route path="/" element={<CatalogPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/filmes/:id" element={<MovieDetailPage />} />
            <Route
              path="/filmes/novo"
              element={
                <ProtectedRoute>
                  <MovieFormPage mode="create" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/filmes/:id/editar"
              element={
                <ProtectedRoute>
                  <MovieFormPage mode="edit" />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
      </div>
    </AuthProvider>
  );
}
