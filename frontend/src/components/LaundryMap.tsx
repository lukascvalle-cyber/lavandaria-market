import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { ExternalLink, Star } from "lucide-react";
import type { Laundry } from "../types";

interface Props {
  laundries: Laundry[];
}

function markerColor(reviews: number): string {
  if (reviews >= 200) return "#16a34a";
  if (reviews >= 100) return "#2563eb";
  if (reviews >= 30) return "#d97706";
  return "#9ca3af";
}

function markerRadius(reviews: number): number {
  if (reviews >= 200) return 10;
  if (reviews >= 100) return 7;
  if (reviews >= 30) return 5;
  return 4;
}

export default function LaundryMap({ laundries }: Props) {
  const validLaundries = laundries.filter((l) => l.latitude && l.longitude);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <MapContainer
        center={[39.5, -8.0]}
        zoom={7}
        style={{ height: "600px", width: "100%" }}
        scrollWheelZoom
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        {validLaundries.map((l) => (
          <CircleMarker
            key={l.place_id}
            center={[l.latitude, l.longitude]}
            radius={markerRadius(l.reviews_count)}
            pathOptions={{
              fillColor: markerColor(l.reviews_count),
              color: markerColor(l.reviews_count),
              fillOpacity: 0.85,
              weight: 1,
            }}
          >
            <Popup>
              <div className="min-w-[180px]">
                <p className="font-semibold text-gray-900 mb-1">{l.name}</p>
                <p className="text-xs text-gray-500 mb-2">{l.city}, {l.region}</p>
                <div className="flex items-center gap-3 mb-2">
                  {l.rating !== null && (
                    <span className="flex items-center gap-1 text-yellow-600 text-xs font-medium">
                      <Star className="w-3 h-3 fill-yellow-400 stroke-yellow-400" />
                      {l.rating.toFixed(1)}
                    </span>
                  )}
                  <span className="text-xs text-gray-600 font-medium">
                    {l.reviews_count.toLocaleString("pt-PT")} reviews
                  </span>
                </div>
                <a
                  href={l.google_maps_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-xs text-blue-600 hover:underline"
                >
                  <ExternalLink className="w-3 h-3" />
                  Ver no Google Maps
                </a>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 flex items-center gap-6 text-xs text-gray-500">
        <span className="font-medium">{validLaundries.length} localizações</span>
        <div className="flex items-center gap-4">
          {[
            { color: "#16a34a", label: "200+ reviews" },
            { color: "#2563eb", label: "100–199" },
            { color: "#d97706", label: "30–99" },
            { color: "#9ca3af", label: "< 30" },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-1.5">
              <span
                className="w-3 h-3 rounded-full inline-block"
                style={{ background: item.color }}
              />
              {item.label}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
