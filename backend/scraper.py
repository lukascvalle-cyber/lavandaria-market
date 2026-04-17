import os
import sys
import time
import requests
from dotenv import load_dotenv
from database import SessionLocal, Laundry
from datetime import datetime

def _p(_msg):
    pass

load_dotenv()
API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

SEARCH_TERMS = [
    "lavandaria self service",
    "lavandaria automática",
    "self laundry",
    "lava e seca automático",
]

CITIES = [
    "Lisboa", "Porto", "Braga", "Coimbra", "Aveiro", "Leiria",
    "Setúbal", "Faro", "Évora", "Beja", "Portalegre", "Santarém",
    "Castelo Branco", "Guarda", "Viseu", "Vila Real", "Bragança",
    "Viana do Castelo", "Funchal", "Ponta Delgada", "Almada", "Amadora",
    "Sintra", "Cascais", "Loures", "Odivelas", "Vila Franca de Xira",
    "Barreiro", "Seixal", "Matosinhos", "Gaia", "Gondomar",
]

TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def text_search(query: str, page_token: str = None) -> dict:
    params = {"query": query, "key": API_KEY, "language": "pt", "region": "pt"}
    if page_token:
        params["pagetoken"] = page_token
    return requests.get(TEXT_SEARCH_URL, params=params).json()


def get_place_details(place_id: str) -> dict:
    params = {
        "place_id": place_id,
        "key": API_KEY,
        "fields": "name,formatted_address,geometry,rating,user_ratings_total,url,formatted_phone_number,website,address_components",
        "language": "pt",
    }
    return requests.get(DETAILS_URL, params=params).json().get("result", {})


def extract_city_region(address_components: list) -> tuple[str, str]:
    city, region = "", ""
    for comp in address_components:
        types = comp.get("types", [])
        if "locality" in types:
            city = comp["long_name"]
        elif "administrative_area_level_1" in types:
            region = comp["long_name"]
    return city, region


def scrape_all() -> int:
    if not API_KEY:
        raise ValueError("GOOGLE_PLACES_API_KEY not set in .env")

    db = SessionLocal()
    total_new = 0

    try:
        for city in CITIES:
            for term in SEARCH_TERMS:
                query = f"{term} {city} Portugal"
                _p(f"  Searching: {query}")

                page_token = None
                while True:
                    data = text_search(query, page_token)
                    status = data.get("status")

                    if status not in ("OK", "ZERO_RESULTS"):
                        _p(f"    API error: {status} — {data.get('error_message', '')}")
                        break

                    for place in data.get("results", []):
                        place_id = place["place_id"]

                        if db.query(Laundry).filter_by(place_id=place_id).first():
                            continue

                        details = get_place_details(place_id)
                        city_name, region_name = extract_city_region(
                            details.get("address_components", [])
                        )

                        laundry = Laundry(
                            place_id=place_id,
                            name=details.get("name") or place.get("name", ""),
                            address=details.get("formatted_address") or place.get("formatted_address", ""),
                            city=city_name,
                            region=region_name,
                            latitude=place["geometry"]["location"]["lat"],
                            longitude=place["geometry"]["location"]["lng"],
                            rating=details.get("rating") or place.get("rating"),
                            reviews_count=details.get("user_ratings_total") or place.get("user_ratings_total", 0),
                            google_maps_url=details.get("url") or f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                            phone=details.get("formatted_phone_number"),
                            website=details.get("website"),
                            search_term=term,
                            scraped_at=datetime.utcnow(),
                        )
                        db.add(laundry)
                        total_new += 1
                        _p(f"    + {laundry.name} ({laundry.reviews_count} reviews)")

                    db.commit()

                    page_token = data.get("next_page_token")
                    if not page_token:
                        break
                    time.sleep(2)  # Required delay before using next_page_token

                time.sleep(0.3)
    finally:
        db.close()

    _p(f"\nDone! Added {total_new} new laundries.")
    return total_new


if __name__ == "__main__":
    scrape_all()
