import { useEffect, useState, useMemo } from "react";
import { Download, Table2, Map, Loader2 } from "lucide-react";
import type { Laundry, Stats, FilterOptions } from "./types";
import StatsBar from "./components/StatsBar";
import Filters from "./components/Filters";
import LaundryTable from "./components/LaundryTable";
import LaundryMap from "./components/LaundryMap";

type View = "table" | "map";

function computeStats(data: Laundry[]): Stats {
  const byRegion: Record<string, number> = {};
  let ratingSum = 0;
  let ratingCount = 0;

  for (const l of data) {
    if (l.region) byRegion[l.region] = (byRegion[l.region] ?? 0) + 1;
    if (l.rating != null) { ratingSum += l.rating; ratingCount++; }
  }

  const sorted = [...data].sort((a, b) => b.reviews_count - a.reviews_count);

  return {
    total: data.length,
    avg_rating: ratingCount > 0 ? Math.round((ratingSum / ratingCount) * 100) / 100 : null,
    by_region: Object.entries(byRegion)
      .map(([region, count]) => ({ region, count }))
      .sort((a, b) => b.count - a.count),
    top_laundry: sorted[0]
      ? { name: sorted[0].name, reviews_count: sorted[0].reviews_count, city: sorted[0].city, rating: sorted[0].rating }
      : null,
  };
}

function computeFilterOptions(data: Laundry[]): FilterOptions {
  return {
    regions: [...new Set(data.map(l => l.region).filter(Boolean))].sort(),
    cities: [...new Set(data.map(l => l.city).filter(Boolean))].sort(),
  };
}

function exportCsv(data: Laundry[]) {
  const header = ["Nome","Cidade","Região","Morada","Avaliação","Nº Reviews","Telefone","Website","Google Maps"];
  const rows = data.map(l => [
    l.name, l.city, l.region, l.address,
    l.rating ?? "", l.reviews_count,
    l.phone ?? "", l.website ?? "", l.google_maps_url,
  ]);
  const csv = [header, ...rows]
    .map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(","))
    .join("\n");
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "lavanderias_portugal.csv"; a.click();
  URL.revokeObjectURL(url);
}

export default function App() {
  const [allData, setAllData] = useState<Laundry[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<View>("table");

  const [region, setRegion] = useState("");
  const [city, setCity] = useState("");
  const [search, setSearch] = useState("");
  const [minReviews, setMinReviews] = useState("");

  useEffect(() => {
    fetch("/laundries.json")
      .then(r => r.json())
      .then((data: Laundry[]) => { setAllData(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    let d = allData;
    if (region) d = d.filter(l => l.region === region);
    if (city) d = d.filter(l => l.city === city);
    if (search) d = d.filter(l => l.name.toLowerCase().includes(search.toLowerCase()));
    if (minReviews) d = d.filter(l => l.reviews_count >= Number(minReviews));
    return d;
  }, [allData, region, city, search, minReviews]);

  const stats = useMemo(() => computeStats(filtered), [filtered]);
  const filterOptions = useMemo(() => computeFilterOptions(allData), [allData]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <header className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Lavanderias Self-Service — Portugal
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              Ranking por número de avaliações no Google Maps
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => exportCsv(filtered)}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-gray-600"
            >
              <Download className="w-4 h-4" />
              CSV
            </button>
          </div>
        </header>

        <StatsBar stats={stats} />

        <Filters
          filters={filterOptions}
          region={region}
          city={city}
          search={search}
          minReviews={minReviews}
          onRegionChange={setRegion}
          onCityChange={setCity}
          onSearchChange={setSearch}
          onMinReviewsChange={setMinReviews}
          onClear={() => { setRegion(""); setCity(""); setSearch(""); setMinReviews(""); }}
        />

        <div className="flex items-center gap-2 mb-4">
          <button
            onClick={() => setView("table")}
            className={`flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-colors ${
              view === "table"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            <Table2 className="w-4 h-4" />
            Tabela
          </button>
          <button
            onClick={() => setView("map")}
            className={`flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-colors ${
              view === "map"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            <Map className="w-4 h-4" />
            Mapa
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-24">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        ) : view === "table" ? (
          <LaundryTable laundries={filtered} />
        ) : (
          <LaundryMap laundries={filtered} />
        )}
      </div>
    </div>
  );
}
