// ============================================================================
// Dashboard Store
// Zustand store for dashboard/recruiter view
// ============================================================================

import { create } from 'zustand';
import type { Candidate } from '../types';
import api from '../services/api';

interface Filters {
  role: string | null;
  search: string;
  page: number;
  limit: number;
}

interface DashboardStore {
  candidates: Candidate[];
  totalCount: number;
  filters: Filters;
  loading: boolean;
  error: string | null;
  
  fetchCandidates: () => Promise<void>;
  setFilter: (key: keyof Filters, value: any) => void;
  deleteCandidate: (id: number) => Promise<void>;
  reset: () => void;
}

const initialFilters: Filters = {
  role: null,
  search: '',
  page: 1,
  limit: 10,
};

export const useDashboardStore = create<DashboardStore>((set, get) => ({
  candidates: [],
  totalCount: 0,
  filters: initialFilters,
  loading: false,
  error: null,

  fetchCandidates: async () => {
    const { filters } = get();
    set({ loading: true, error: null });
    
    try {
      const skip = (filters.page - 1) * filters.limit;
      const params: any = {
        skip,
        limit: filters.limit,
      };
      
      if (filters.role) {
        params.role = filters.role;
      }

      const data = await api.getCandidates(params);
      
      // Client-side search if needed
      let candidates = data.items || [];
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        candidates = candidates.filter(
          (c) =>
            c.name.toLowerCase().includes(searchLower) ||
            c.email.toLowerCase().includes(searchLower) ||
            c.github_url.toLowerCase().includes(searchLower)
        );
      }

      set({
        candidates,
        totalCount: data.total || candidates.length,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch candidates';
      set({ error: errorMessage, candidates: [], totalCount: 0 });
    } finally {
      set({ loading: false });
    }
  },

  setFilter: (key: keyof Filters, value: any) => {
    set((state) => ({
      filters: {
        ...state.filters,
        [key]: value,
        // Reset page when changing other filters
        page: key === 'page' ? value : 1,
      },
    }));
    
    // Auto-fetch when filters change
    get().fetchCandidates();
  },

  deleteCandidate: async (id: number) => {
    set({ loading: true, error: null });
    try {
      await api.deleteCandidate(id);
      await get().fetchCandidates(); // Refresh list
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete candidate';
      set({ error: errorMessage });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  reset: () => {
    set({
      candidates: [],
      totalCount: 0,
      filters: initialFilters,
      loading: false,
      error: null,
    });
  },
}));
