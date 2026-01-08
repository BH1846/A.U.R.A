/**
 * Authentication Context for I-Intern integration
 * Manages JWT tokens and user authentication state
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface User {
  id: number;
  email: string;
  name: string;
  role: 'student' | 'recruiter' | 'admin';
  companyId?: number;
  companyName?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
  isStudent: () => boolean;
  isRecruiter: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'aura_auth_token';

/**
 * Decode JWT token to extract user information
 * Note: This is a simple decode, not validation (validation happens on backend)
 */
function decodeToken(token: string): User | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    const payload = JSON.parse(atob(parts[1]));
    
    return {
      id: payload.id || 0,
      email: payload.email || '',
      name: payload.name || '',
      role: payload.role || 'student',
      companyId: payload.company_id,
      companyName: payload.company_name
    };
  } catch (error) {
    console.error('Failed to decode token:', error);
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for token in localStorage or URL params (for I-Intern integration)
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');

    console.log('AuthContext: Checking for token');
    console.log('Stored token:', storedToken ? 'exists' : 'none');
    console.log('URL token:', urlToken ? 'exists' : 'none');

    const tokenToUse = urlToken || storedToken;

    if (tokenToUse) {
      const decodedUser = decodeToken(tokenToUse);
      if (decodedUser) {
        console.log('AuthContext: Token decoded successfully', decodedUser);
        setToken(tokenToUse);
        setUser(decodedUser);
        localStorage.setItem(TOKEN_KEY, tokenToUse);
        
        // Remove token from URL if present
        if (urlToken) {
          window.history.replaceState({}, document.title, window.location.pathname);
        }
      } else {
        console.error('AuthContext: Failed to decode token');
      }
    } else {
      console.warn('AuthContext: No token found');
    }

    setIsLoading(false);
  }, []);

  const login = (newToken: string) => {
    const decodedUser = decodeToken(newToken);
    if (decodedUser) {
      setToken(newToken);
      setUser(decodedUser);
      localStorage.setItem(TOKEN_KEY, newToken);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
  };

  const isStudent = () => user?.role === 'student';
  const isRecruiter = () => user?.role === 'recruiter';

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    isLoading,
    login,
    logout,
    isStudent,
    isRecruiter
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * Hook to get authorization header for API requests
 */
export function useAuthHeader() {
  const { token } = useAuth();
  
  return token ? { Authorization: `Bearer ${token}` } : {};
}
