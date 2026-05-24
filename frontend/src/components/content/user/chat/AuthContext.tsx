import React, { createContext, useContext } from 'react';
import type { ReactNode } from 'react';
import { jwtDecode } from 'jwt-decode';

type Auth = { token: string; email: string };

const getAuth = (): Auth => {
  const token = localStorage.getItem('token') || '';
  try {
    const payload = jwtDecode<{ sub: string }>(token);
    return { token, email: payload.sub };
  } catch {
    return { token: '', email: '' };
  }
};

const AuthContext = createContext<Auth>(getAuth());

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const auth = getAuth();
  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);