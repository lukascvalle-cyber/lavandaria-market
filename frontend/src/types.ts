export interface Laundry {
  place_id: string;
  name: string;
  address: string;
  city: string;
  region: string;
  latitude: number;
  longitude: number;
  rating: number | null;
  reviews_count: number;
  google_maps_url: string;
  phone: string | null;
  website: string | null;
}

export interface Stats {
  total: number;
  avg_rating: number | null;
  by_region: { region: string; count: number }[];
  top_laundry: {
    name: string;
    reviews_count: number;
    city: string;
    rating: number | null;
  } | null;
}

export interface FilterOptions {
  regions: string[];
  cities: string[];
}
