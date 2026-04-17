import { Search, X } from "lucide-react";
import type { FilterOptions } from "../types";

interface Props {
  filters: FilterOptions | null;
  region: string;
  city: string;
  search: string;
  minReviews: string;
  onRegionChange: (v: string) => void;
  onCityChange: (v: string) => void;
  onSearchChange: (v: string) => void;
  onMinReviewsChange: (v: string) => void;
  onClear: () => void;
}

export default function Filters({
  filters,
  region,
  city,
  search,
  minReviews,
  onRegionChange,
  onCityChange,
  onSearchChange,
  onMinReviewsChange,
  onClear,
}: Props) {
  const hasFilters = region || city || search || minReviews;

  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 mb-4">
      <div className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[180px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Pesquisar nome</label>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Ex: Wash & Go"
              className="w-full pl-8 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="min-w-[160px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Região</label>
          <select
            value={region}
            onChange={(e) => onRegionChange(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas as regiões</option>
            {filters?.regions.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>

        <div className="min-w-[160px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Cidade</label>
          <select
            value={city}
            onChange={(e) => onCityChange(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas as cidades</option>
            {filters?.cities.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <div className="min-w-[130px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Mín. reviews</label>
          <input
            type="number"
            value={minReviews}
            onChange={(e) => onMinReviewsChange(e.target.value)}
            placeholder="Ex: 50"
            min={0}
            className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {hasFilters && (
          <button
            onClick={onClear}
            className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-500 hover:text-gray-700 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <X className="w-4 h-4" />
            Limpar
          </button>
        )}
      </div>
    </div>
  );
}
