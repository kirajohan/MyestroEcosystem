// components/broadcast/AudienceSelector.tsx
"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import type { UserResponse } from "@/lib/types";
import { useAudienceSelection, type FilterState, DEFAULT_FILTER } from "@/hooks/useAudienceSelection";

const API_BASE = "/api";

interface AudienceSelectorProps {
  onSelectionChange: (ids: number[] | "all", filter?: FilterState) => void;
}

export default function AudienceSelector({ onSelectionChange }: AudienceSelectorProps) {
  const {
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
  } = useAudienceSelection();

  const [users, setUsers] = useState<UserResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const PAGE_SIZE = 20;

  const fetchUsers = useCallback(async (f: FilterState, p: number) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("skip", String(p * PAGE_SIZE));
      params.set("limit", String(PAGE_SIZE));
      if (f.search) params.set("search", f.search);
      if (f.role) params.set("role", f.role);
      if (f.cefr_level) params.set("cefr_level", f.cefr_level);
      if (f.lang) params.set("lang", f.lang);
      if (f.is_active) params.set("is_active", f.is_active);

      const res = await fetch(`${API_BASE}/users?${params.toString()}`);
      if (!res.ok) throw new Error("Failed to fetch users");
      const data = await res.json();
      setUsers(data.data || []);
      setTotal(data.total || 0);
    } catch (e) {
      console.error("AudienceSelector fetch error:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setPage(0);
      fetchUsers(filters, 0);
    }, 400);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [filters, fetchUsers]);

  // Page change
  useEffect(() => {
    fetchUsers(filters, page);
  }, [page, fetchUsers, filters]);

  // Notify parent on selection change
  useEffect(() => {
    if (selectAllFiltered) {
      onSelectionChange("all", filters);
    } else {
      onSelectionChange(Array.from(selectedIds));
    }
  }, [selectedIds, selectAllFiltered, filters, onSelectionChange]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-800">
          Qabul qiluvchilar ({totalSelected === "all" ? `${total} ta (barcha)` : `${totalSelected} ta tanlangan`})
        </h3>
        {totalSelected !== 0 && (
          <button
            onClick={clearAll}
            className="text-xs text-rose-600 hover:text-rose-800"
          >
            Tozalash
          </button>
        )}
      </div>

      {/* Filter bar */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <input
          className="rounded border border-gray-300 px-2 py-1.5 text-xs"
          placeholder="Qidirish (ism/email)..."
          value={filters.search}
          onChange={(e) => updateFilter({ search: e.target.value })}
        />
        <select
          className="rounded border border-gray-300 px-2 py-1.5 text-xs"
          value={filters.role}
          onChange={(e) => updateFilter({ role: e.target.value })}
        >
          <option value="">Barcha rollar</option>
          <option value="user">User</option>
          <option value="admin">Admin</option>
        </select>
        <select
          className="rounded border border-gray-300 px-2 py-1.5 text-xs"
          value={filters.cefr_level}
          onChange={(e) => updateFilter({ cefr_level: e.target.value })}
        >
          <option value="">Barcha darajalar</option>
          <option value="A1">A1</option>
          <option value="A2">A2</option>
          <option value="B1">B1</option>
          <option value="B2">B2</option>
          <option value="C1">C1</option>
          <option value="C2">C2</option>
        </select>
        <select
          className="rounded border border-gray-300 px-2 py-1.5 text-xs"
          value={filters.is_active}
          onChange={(e) => updateFilter({ is_active: e.target.value })}
        >
          <option value="">Barcha holatlar</option>
          <option value="true">Faol</option>
          <option value="false">Bloklangan</option>
        </select>
      </div>

      {/* Select all filtered banner */}
      {total > 0 && !selectAllFiltered && (
        <button
          onClick={enableSelectAllFiltered}
          className="w-full rounded bg-primary-50 py-1.5 text-xs font-medium text-primary hover:bg-primary-100"
        >
          Filtr bo&#39;yicha barcha {total} foydalanuvchini tanlash
        </button>
      )}
      {selectAllFiltered && (
        <div className="rounded bg-emerald-50 py-1.5 text-center text-xs font-medium text-emerald-700">
          Barcha {total} foydalanuvchi tanlandi
        </div>
      )}

      {/* User table */}
      <div className="max-h-80 overflow-y-auto">
        {loading ? (
          <div className="py-8 text-center text-sm text-gray-400">Yuklanmoqda...</div>
        ) : users.length === 0 ? (
          <div className="py-8 text-center text-sm text-gray-400">Foydalanuvchi topilmadi</div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead className="sticky top-0 bg-gray-50">
              <tr className="text-gray-500">
                <th className="w-8 p-2">
                  <input
                    type="checkbox"
                    checked={users.every((u) => selectedIds.has(u.id))}
                    onChange={() => {
                      if (users.every((u) => selectedIds.has(u.id))) {
                        // Deselect all on page
                        for (const u of users) {
                          if (selectedIds.has(u.id)) toggle(u.id);
                        }
                      } else {
                        selectAllOnPage(users.map((u) => u.id));
                      }
                    }}
                    className="h-3.5 w-3.5 rounded border-gray-300"
                  />
                </th>
                <th className="p-2 font-medium">Ism</th>
                <th className="p-2 font-medium">Email</th>
                <th className="p-2 font-medium">Rol</th>
                <th className="p-2 font-medium">CEFR</th>
                <th className="p-2 font-medium">Holat</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr
                  key={user.id}
                  className={`border-t border-gray-100 hover:bg-gray-50 ${
                    selectedIds.has(user.id) ? "bg-primary-50" : ""
                  }`}
                >
                  <td className="p-2">
                    <input
                      type="checkbox"
                      checked={selectedIds.has(user.id)}
                      onChange={() => toggle(user.id)}
                      className="h-3.5 w-3.5 rounded border-gray-300"
                    />
                  </td>
                  <td className="p-2 font-medium text-gray-800">{user.full_name}</td>
                  <td className="p-2 text-gray-500">{user.email}</td>
                  <td className="p-2 text-gray-500">{user.role}</td>
                  <td className="p-2 text-gray-500">{user.cefr_level || "-"}</td>
                  <td className="p-2">
                    <span
                      className={`inline-block rounded-full px-1.5 py-0.5 text-[10px] font-medium ${
                        user.is_active
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-rose-100 text-rose-700"
                      }`}
                    >
                      {user.is_active ? "Faol" : "Blok"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            {page * PAGE_SIZE + 1}-{Math.min((page + 1) * PAGE_SIZE, total)} / {total}
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="rounded border border-gray-300 px-2 py-1 disabled:opacity-40"
            >
              ←
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="rounded border border-gray-300 px-2 py-1 disabled:opacity-40"
            >
              →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}