import { ExternalLink, Phone, Globe, Star } from "lucide-react";
import type { Laundry } from "../types";

interface Props {
  laundries: Laundry[];
}

function Stars({ rating }: { rating: number | null }) {
  if (rating === null) return <span className="text-gray-300 text-xs">—</span>;
  return (
    <span className="flex items-center gap-1 text-sm font-medium text-yellow-600">
      <Star className="w-3.5 h-3.5 fill-yellow-400 stroke-yellow-400" />
      {rating.toFixed(1)}
    </span>
  );
}

export default function LaundryTable({ laundries }: Props) {
  if (laundries.length === 0) {
    return (
      <div className="bg-white rounded-xl p-12 text-center shadow-sm border border-gray-100">
        <p className="text-gray-400 text-sm">Sem resultados para os filtros selecionados.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-100">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 w-12">#</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Nome</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Cidade</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Região</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Avaliação</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Reviews</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Contactos</th>
            </tr>
          </thead>
          <tbody>
            {laundries.map((l, i) => (
              <tr
                key={l.place_id}
                className="border-b border-gray-50 hover:bg-blue-50/30 transition-colors"
              >
                <td className="px-4 py-3 text-gray-400 font-mono text-xs">{i + 1}</td>
                <td className="px-4 py-3 max-w-[220px]">
                  <a
                    href={l.google_maps_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-blue-600 hover:underline flex items-start gap-1.5 group"
                  >
                    <span className="truncate">{l.name}</span>
                    <ExternalLink className="w-3 h-3 mt-0.5 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                  <p className="text-xs text-gray-400 truncate mt-0.5">{l.address}</p>
                </td>
                <td className="px-4 py-3 text-gray-600">{l.city || "—"}</td>
                <td className="px-4 py-3 text-gray-500 text-xs">
                  {l.region ? (
                    <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                      {l.region}
                    </span>
                  ) : "—"}
                </td>
                <td className="px-4 py-3">
                  <Stars rating={l.rating} />
                </td>
                <td className="px-4 py-3">
                  <span className={`font-semibold ${
                    l.reviews_count >= 100
                      ? "text-green-600"
                      : l.reviews_count >= 30
                      ? "text-blue-600"
                      : "text-gray-500"
                  }`}>
                    {l.reviews_count.toLocaleString("pt-PT")}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    {l.phone && (
                      <a
                        href={`tel:${l.phone}`}
                        className="text-gray-400 hover:text-green-600 transition-colors"
                        title={l.phone}
                      >
                        <Phone className="w-4 h-4" />
                      </a>
                    )}
                    {l.website && (
                      <a
                        href={l.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-blue-600 transition-colors"
                        title={l.website}
                      >
                        <Globe className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 text-xs text-gray-400">
        {laundries.length.toLocaleString("pt-PT")} resultados
      </div>
    </div>
  );
}
