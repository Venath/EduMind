import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// Types
export interface DashboardStats {
    students: number;
    courses: number;
    resources: number;
    averagePerformance: number;
}

export interface AdminFilters {
    dateRange?: {
        start: Date;
        end: Date;
    };
    courseId?: string;
    status?: 'active' | 'inactive' | 'all';
    searchQuery?: string;
}

interface AdminState {
    // Dashboard data
    stats: DashboardStats;

    // UI state
    selectedCourse: string | null;
    filters: AdminFilters;
    viewMode: 'grid' | 'list';

    // Loading states
    isLoadingStats: boolean;

    // Actions
    setStats: (stats: DashboardStats) => void;
    setSelectedCourse: (courseId: string | null) => void;
    updateFilters: (filters: Partial<AdminFilters>) => void;
    clearFilters: () => void;
    setViewMode: (mode: 'grid' | 'list') => void;
    setLoadingStats: (isLoading: boolean) => void;
}

export const useAdminStore = create<AdminState>()(
    devtools(
        persist(
            (set) => ({
                // Initial state
                stats: {
                    students: 0,
                    courses: 0,
                    resources: 0,
                    averagePerformance: 0,
                },
                selectedCourse: null,
                filters: {},
                viewMode: 'grid',
                isLoadingStats: false,

                // Actions
                setStats: (stats) =>
                    set({ stats }, false, 'setStats'),

                setSelectedCourse: (courseId) =>
                    set({ selectedCourse: courseId }, false, 'setSelectedCourse'),

                updateFilters: (newFilters) =>
                    set(
                        (state) => ({
                            filters: { ...state.filters, ...newFilters },
                        }),
                        false,
                        'updateFilters'
                    ),

                clearFilters: () =>
                    set({ filters: {} }, false, 'clearFilters'),

                setViewMode: (mode) =>
                    set({ viewMode: mode }, false, 'setViewMode'),

                setLoadingStats: (isLoading) =>
                    set({ isLoadingStats: isLoading }, false, 'setLoadingStats'),
            }),
            {
                name: 'admin-storage',
                partialize: (state) => ({
                    viewMode: state.viewMode,
                    filters: state.filters,
                }),
            }
        ),
        { name: 'AdminStore' }
    )
);
