import axios from "axios";
import type {
  DashboardStats,
  MovieDetail,
  MovieFormData,
  MovieListItem,
  Page,
  ReviewFormData,
} from "../types/movie";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  withCredentials: true, // envia/recebe o cookie de sessão do Administrador
});

export interface ListMoviesParams {
  page?: number;
  size?: number;
  q?: string;
  genero?: string;
}

export async function fetchMovies(params: ListMoviesParams): Promise<Page<MovieListItem>> {
  const { data } = await api.get<Page<MovieListItem>>("/movies", { params });
  return data;
}

export async function fetchMovie(id: string): Promise<MovieDetail> {
  const { data } = await api.get<MovieDetail>(`/movies/${id}`);
  return data;
}

export async function createMovie(payload: MovieFormData): Promise<MovieDetail> {
  const { data } = await api.post<MovieDetail>("/movies", payload);
  return data;
}

export async function updateMovie(id: string, payload: MovieFormData): Promise<MovieDetail> {
  const { data } = await api.put<MovieDetail>(`/movies/${id}`, payload);
  return data;
}

export async function deleteMovie(id: string): Promise<void> {
  await api.delete(`/movies/${id}`);
}

export async function fetchGenres(): Promise<string[]> {
  const { data } = await api.get<string[]>("/genres");
  return data;
}

export async function addReview(movieId: string, payload: ReviewFormData): Promise<void> {
  await api.post(`/movies/${movieId}/reviews`, payload);
}

export async function fetchDashboard(): Promise<DashboardStats> {
  const { data } = await api.get<DashboardStats>("/dashboard");
  return data;
}

export interface AdminOut {
  id: string;
  nome: string;
  email: string;
}

export async function login(email: string, senha: string): Promise<AdminOut> {
  const { data } = await api.post<AdminOut>("/auth/login", { email, senha });
  return data;
}

export async function logout(): Promise<void> {
  await api.post("/auth/logout");
}

export async function fetchCurrentAdmin(): Promise<AdminOut | null> {
  try {
    const { data } = await api.get<AdminOut>("/auth/me");
    return data;
  } catch {
    return null;
  }
}

export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((item) => item.msg ?? JSON.stringify(item)).join(", ");
    }
    if (error.message) return error.message;
  }
  return "Ocorreu um erro inesperado. Tente novamente.";
}

export default api;
