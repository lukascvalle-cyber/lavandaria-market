import { useEffect, useState, useCallback } from "react";
import { Download, RefreshCw, Table2, Map, Loader2 } from "lucide-react";
import type { Laundry, Stats, FilterOptions } from "./types";
import { apiUrl } from "./api";
import StatsBar from "./components/StatsBar";
import Filters from "./components/Filters";
import LaundryTable from "./components/LaundryTable";
import LaundryMap from "./components/LaundryMap";

type View = "table" | "map";

export default function App() {
  const [laundries, setLaundries] = useState<Laundry[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [scrapeError, setScrapeError] = useState<string | null>(null);
  const [view, setView] = useState<View>("table");

  const [region, setRegion] = useState("");
  const [city, setCity] = useState("");
  const [search, setSearch] = useState("");
  const [minReviews, setMinReviews] = useState("");

  const fetchLaundries = useCallback(async () => {
    const params = new URLSearchParams();
    if (region) params.set("region", region);
    if (city) params.set("city", city);
    if (search) params.set("search", search);
    if (minReviews) params.set("min_reviews", minReviews);

    const res = await fetch(apiUrl(`/api/laundries?${params}`));
    const data = await res.json();
    setLaundries(data);
  }, [region, city, search, minReviews]);

  useEffect(() => {
    Promise.all([
      fetch(apiUrl("/api/stats")).then((r) => r.json()),
      fetch(apiUrl("/api/filters")).then((r) => r.json()),
    ]).then(([statsData, filtersData]) => {
      setStats(statsData);
      setFilterOptions(filtersData);
    });
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchLaundries().finally(() => setLoading(false));
  }, [fetchLaundries]);

  async function handleScrape() {
    setScraping(true);
    setScrapeError(null);
    try {
      await fetch(apiUrl("/api/scrape"), { method: "POST" });
      const poll = setInterval(async () => {
        const res = await fetch(apiUrl("/api/scrape/status"));
        const status = await res.json();
        if (!status.running) {
          clearInterval(poll);
          setScraping(false);
          if (status.error) {
            setScrapeError(status.error);
          } else {
            await Promise.all([
              fetch(apiUrl("/api/stats")).then((r) => r.json()).then(setStats),
              fetch(apiUrl("/api/filters")).then((r) => r.json()).then(setFilterOptions),
              fetchLaundries(),
            ]);
          }
        }
      }, 3000);
    } catch {
      setScraping(false);
    }
  }

  function clearFilters() {
    setRegion("");
    setCity("");
    setSearch("");
    setMinReviews("");
  }

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
            <a
              href={apiUrl("/api/export/csv")}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-gray-600"
            >
              <Download className="w-4 h-4" />
              CSV
            </a>
            <a
              href={apiUrl("/api/export/excel")}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-gray-600"
            >
              <Download className="w-4 h-4" />
              Excel
            </a>
            <button
              onClick={handleScrape}
              disabled={scraping}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {scraping ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4" />
              )}
              {scraping ? "A recolher dados..." : "Recolher dados"}
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
          onClear={clearFilters}
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

        {scrapeError && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            <strong>Erro no scraping:</strong> {scrapeError}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-24">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        ) : view === "table" ? (
          <LaundryTable laundries={laundries} />
        ) : (
          <LaundryMap laundries={laundries} />
        )}
      </div>
    </div>
  );
}
