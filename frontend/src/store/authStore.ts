import { create } from 'zustand';
import { authAPI } from '@/api/client';
import type { User, LoginCredentials } from '@/types';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (credentials: LoginCredentials) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.login(credentials);
      const token = response.access_token;
      
      // Store token in localStorage
      localStorage.setItem('access_token', token);
      
      // Fetch user data
      const user = await authAPI.getCurrentUser();
      
      set({ user, token, isLoading: false });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Login failed. Please try again.';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  logout: () => {
    // Clear localStorage
    localStorage.removeItem('access_token');
    
    // Clear state
    set({ user: null, token: null, error: null });
  },

  fetchCurrentUser: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ user: null, token: null });
      return;
    }

    set({ isLoading: true });
    try {
      const user = await authAPI.getCurrentUser();
      set({ user, token, isLoading: false });
    } catch (error) {
      // Token is invalid, clear it
      localStorage.removeItem('access_token');
      set({ user: null, token: null, isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
