import {
    createContext,
    useContext,
    useState,
    type ReactNode,
  } from "react";
  import api from "../services/api";
  
  export interface User {
    id: string;
    name: string;
    email: string;
  }
  
  interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (
      name: string,
      email: string,
      password: string
    ) => Promise<void>;
    logout: () => void;
  }
  
  interface AuthResponse {
    access_token: string;
    token_type: string;
    user: {
      id: number;
      name: string;
      email: string;
    };
  }
  
  const AuthContext = createContext<AuthContextType | undefined>(undefined);
  
  function getApiError(error: unknown): string {
    if (
      typeof error === "object" &&
      error !== null &&
      "response" in error
    ) {
      const response = (error as {
        response?: {
          data?: {
            detail?: string;
          };
        };
      }).response;
  
      if (response?.data?.detail) {
        return response.data.detail;
      }
    }
  
    return "Unable to connect to the server. Please try again.";
  }
  
  function saveAuthData(data: AuthResponse): User {
    const user: User = {
      id: String(data.user.id),
      name: data.user.name,
      email: data.user.email,
    };
  
    localStorage.setItem("truthcams_access_token", data.access_token);
    localStorage.setItem("truthcams_user", JSON.stringify(user));
  
    return user;
  }
  
  export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(() => {
      const savedUser = localStorage.getItem("truthcams_user");
  
      try {
        return savedUser ? JSON.parse(savedUser) : null;
      } catch {
        localStorage.removeItem("truthcams_user");
        localStorage.removeItem("truthcams_access_token");
        return null;
      }
    });
  
    const login = async (email: string, password: string) => {
      try {
        const response = await api.post<AuthResponse>("/auth/login", {
          email,
          password,
        });
  
        const authenticatedUser = saveAuthData(response.data);
        setUser(authenticatedUser);
      } catch (error) {
        throw new Error(getApiError(error));
      }
    };
  
    const register = async (
      name: string,
      email: string,
      password: string
    ) => {
      try {
        await api.post("/auth/register", {
          name,
          email,
          password,
        });
  
        // Automatically log in after successful registration
        await login(email, password);
      } catch (error) {
        throw new Error(getApiError(error));
      }
    };
  
    const logout = () => {
      setUser(null);
      localStorage.removeItem("truthcams_user");
      localStorage.removeItem("truthcams_access_token");
    };
  
    return (
      <AuthContext.Provider
        value={{
          user,
          isAuthenticated: Boolean(user),
          login,
          register,
          logout,
        }}
      >
        {children}
      </AuthContext.Provider>
    );
  }
  
  export function useAuth() {
    const context = useContext(AuthContext);
  
    if (!context) {
      throw new Error("useAuth must be used within AuthProvider");
    }
  
    return context;
  }