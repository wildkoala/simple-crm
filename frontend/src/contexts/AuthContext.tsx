import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, getCurrentUser, login as apiLogin, LoginCredentials, setAuthToken, clearAuthToken, getAuthToken } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAdmin: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const isAdmin = user?.role === 'admin';

  const logout = useCallback(() => {
    clearAuthToken();
    setUser(null);
    navigate('/login');
  }, [navigate]);

  useEffect(() => {
    // Check if user is already logged in
    const token = getAuthToken();
    if (token) {
      getCurrentUser()
        .then(setUser)
        .catch(() => {
          clearAuthToken();
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  // Listen for 401 unauthorized events from the API client
  useEffect(() => {
    const handleUnauthorized = () => {
      setUser(null);
      navigate('/login');
    };
    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, [navigate]);

  const login = async (credentials: LoginCredentials) => {
    const { access_token } = await apiLogin(credentials);
    setAuthToken(access_token);
    const userData = await getCurrentUser();
    setUser(userData);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, isAdmin, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
