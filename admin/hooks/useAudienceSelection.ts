// hooks/useAudienceSelection.ts
"use client";

import { useState, useCallback } from "react";

export interface FilterState {
  search: string;
  role: string;
  cefr_level: string;
  lang: string;
  is_active: string; // "" | "true" | "false"
}

export const DEFAULT_FILTER: FilterState = {
  search: "",
  role: "",
  cefr_level: "",
  lang: "",
  is_active: "",
};

export function useAudienceSelection() {
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [selectAllFiltered, setSelectAllFiltered] = useState(false);
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTER);

  const toggle = useCallback((userId: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(userId)) {
        next.delete(userId);
      } else {
        next.add(userId);
      }
      return next;
    });
    setSelectAllFiltered(false);
  }, []);

  const selectAllOnPage = useCallback((pageIds: number[]) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      for (const id of pageIds) {
        next.add(id);
      }
      return next;
    });
  }, []);

  const clearAll = useCallback(() => {
    setSelectedIds(new Set());
    setSelectAllFiltered(false);
    setFilters(DEFAULT_FILTER);
  }, []);

  const enableSelectAllFiltered = useCallback(() => {
    setSelectAllFiltered(true);
  }, []);

  const disableSelectAllFiltered = useCallback(() => {
    setSelectAllFiltered(false);
  }, []);

  const updateFilter = useCallback((partial: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...partial }));
  }, []);

  const totalSelected = selectAllFiltered ? "all" : selectedIds.size;

  return {
    selectedIds,
    selectAllFiltered,
    filters,
    totalSelected,
    toggle,
    selectAllOnPage,
    clearAll,
    enableSelectAllFiltered,
    disableSelectAllFiltered,
    updateFilter,
    setFilters,
  };
}