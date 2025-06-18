import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface DateRange {
  start: string | null;
  end: string | null;
}

interface FilterState {
  // Date range: Using ISO strings for localStorage compatibility
  dateRange: DateRange;
  selectedRegions: string[];
  selectedBrands: string[];
  selectedCategories: string[];
  selectedStores: string[];

  // Actions
  setDateRange: (start: string | null, end: string | null) => void;
  toggleRegion: (regionId: string) => void;
  toggleBrand: (brandId: string) => void;
  toggleCategory: (categoryId: string) => void;
  toggleStore: (storeId: string) => void;
  clearFilters: () => void;
  // Hydration state (optional, for checking if store is rehydrated)
  _hasHydrated: boolean;
  setHasHydrated: (hydrated: boolean) => void;
}

const initialState = {
  dateRange: { start: null, end: null },
  selectedRegions: [],
  selectedBrands: [],
  selectedCategories: [],
  selectedStores: [],
  _hasHydrated: false,
};

export const useFilterStore = create<FilterState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setDateRange: (start, end) => set({ dateRange: { start, end } }),

      toggleRegion: (regionId) =>
        set((state) => {
          const isSelected = state.selectedRegions.includes(regionId);
          return {
            selectedRegions: isSelected
              ? state.selectedRegions.filter((r) => r !== regionId)
              : [...state.selectedRegions, regionId],
          };
        }),

      toggleBrand: (brandId) =>
        set((state) => {
          const isSelected = state.selectedBrands.includes(brandId);
          return {
            selectedBrands: isSelected
              ? state.selectedBrands.filter((b) => b !== brandId)
              : [...state.selectedBrands, brandId],
          };
        }),

      toggleCategory: (categoryId) =>
        set((state) => {
          const isSelected = state.selectedCategories.includes(categoryId);
          return {
            selectedCategories: isSelected
              ? state.selectedCategories.filter((c) => c !== categoryId)
              : [...state.selectedCategories, categoryId],
          };
        }),

      toggleStore: (storeId) =>
        set((state) => {
          const isSelected = state.selectedStores.includes(storeId);
          return {
            selectedStores: isSelected
              ? state.selectedStores.filter((s) => s !== storeId)
              : [...state.selectedStores, storeId],
          };
        }),

      clearFilters: () => set({
        ...initialState,
        dateRange: {start: null, end: null}, // Explicitly reset dateRange due to object nature
        selectedRegions: [], // Ensure all filter arrays are reset
        selectedBrands: [],
        selectedCategories: [],
        selectedStores: [],
        // _hasHydrated should persist via onRehydrateStorage or initial set
      }),

      setHasHydrated: (hydrated) => set({ _hasHydrated: hydrated }),
    }),
    {
      name: 'scout-analytics-filters', // Name for localStorage item
      storage: createJSONStorage(() => localStorage), // Use localStorage
      onRehydrateStorage: () => (state) => {
        if (state) state.setHasHydrated(true);
      },
      // partialize: (state) => ({ // Optionally, choose what to persist
      //   dateRange: state.dateRange,
      //   selectedRegions: state.selectedRegions,
      //   selectedBrands: state.selectedBrands,
      // }),
    }
  )
);

// Hook to check for hydration (useful for client-only rendering dependent on persisted state)
export const useHasHydrated = () => {
    const store = useFilterStore.getState();
    const [hydrated, setHydrated] = useState(store._hasHydrated);

    useEffect(() => {
      const unsubFinishHydration = useFilterStore.subscribe(
        (state) => state._hasHydrated,
        (hydratedState) => {
          setHydrated(hydratedState);
        }
      );

      // Initial check
      setHydrated(useFilterStore.getState()._hasHydrated);

      return () => {
        unsubFinishHydration();
      };
    }, []);

    return hydrated;
  };
