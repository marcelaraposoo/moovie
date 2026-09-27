import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import {
  fetchCurrentAdmin,
  login as apiLogin,
  logout as apiLogout,
  type AdminOut,
} from "../api/client";

interface AuthContextValue {
  admin: AdminOut | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, senha: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [admin, setAdmin] = useState<AdminOut | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCurrentAdmin()
      .then(setAdmin)
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, senha: string) {
    const loggedIn = await apiLogin(email, senha);
    setAdmin(loggedIn);
  }

  async function logout() {
    await apiLogout();
    setAdmin(null);
  }

  return (
    <AuthContext.Provider value={{ admin, loading, isAuthenticated: admin !== null, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth precisa ser usado dentro de um <AuthProvider>");
  }
  return context;
}
