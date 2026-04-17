import { Star, MapPin, TrendingUp, Award } from "lucide-react";
import type { Stats } from "../types";

interface Props {
  stats: Stats | null;
}

export default function StatsBar({ stats }: Props) {
  if (!stats) return null;

  const cards = [
    {
      icon: <MapPin className="w-5 h-5 text-blue-500" />,
      label: "Total de Lavanderias",
      value: stats.total.toLocaleString("pt-PT"),
    },
    {
      icon: <Star className="w-5 h-5 text-yellow-500" />,
      label: "Avaliação Média",
      value: stats.avg_rating ? `${stats.avg_rating} ★` : "—",
    },
    {
      icon: <TrendingUp className="w-5 h-5 text-green-500" />,
      label: "Regiões com dados",
      value: stats.by_region.length,
    },
    {
      icon: <Award className="w-5 h-5 text-purple-500" />,
      label: "Mais avaliada",
      value: stats.top_laundry
        ? `${stats.top_laundry.reviews_count} reviews`
        : "—",
      sub: stats.top_laundry?.name,
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      {cards.map((c) => (
        <div key={c.label} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-1">
            {c.icon}
            <span className="text-xs text-gray-500">{c.label}</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{c.value}</div>
          {c.sub && (
            <div className="text-xs text-gray-400 truncate mt-0.5">{c.sub}</div>
          )}
        </div>
      ))}
    </div>
  );
}
