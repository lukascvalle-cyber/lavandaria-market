import io
import logging
import os
import sys
from typing import Optional

# Fix Windows charmap encoding for all log handlers so emoji in place names don't crash
for _h in logging.root.handlers:
    if hasattr(_h, "stream") and hasattr(_h.stream, "reconfigure"):
        _h.stream.reconfigure(encoding="utf-8", errors="replace")
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import func

from database import SessionLocal, Laundry, engine
from scraper import scrape_all
from cleaner import run_clean

app = FastAPI(title="Lavandaria Market PT", version="1.0.0")

# CORS: allow localhost in dev + any Vercel domain + custom origin from env
_extra_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
_allowed_origins = [o.strip() for o in [
    "http://localhost:5173",
    "http://localhost:4173",
    *_extra_origins,
] if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)

_scrape_status = {"running": False, "last_count": None, "error": None}


def _fix_logging_encoding():
    for handler in logging.root.handlers:
        if hasattr(handler, "stream") and hasattr(handler.stream, "reconfigure"):
            try:
                handler.stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
    for name in ("sqlalchemy.engine", "urllib3", "requests"):
        logging.getLogger(name).setLevel(logging.CRITICAL)


def _run_scrape():
    _fix_logging_encoding()
    _scrape_status["running"] = True
    _scrape_status["error"] = None
    try:
        count = scrape_all()
        _scrape_status["last_count"] = count
    except Exception as e:
        _scrape_status["error"] = str(e)
    finally:
        _scrape_status["running"] = False


@app.get("/api/laundries")
def get_laundries(
    region: Optional[str] = None,
    city: Optional[str] = None,
    search: Optional[str] = None,
    min_reviews: Optional[int] = None,
    include_excluded: bool = False,
    limit: int = Query(default=1000, le=2000),
):
    db = SessionLocal()
    try:
        q = db.query(Laundry)
        if not include_excluded:
            q = q.filter(Laundry.excluded == False)
        if region:
            q = q.filter(Laundry.region.ilike(f"%{region}%"))
        if city:
            q = q.filter(Laundry.city.ilike(f"%{city}%"))
        if search:
            q = q.filter(Laundry.name.ilike(f"%{search}%"))
        if min_reviews is not None:
            q = q.filter(Laundry.reviews_count >= min_reviews)

        results = q.order_by(Laundry.reviews_count.desc()).limit(limit).all()
        return [_serialize(r) for r in results]
    finally:
        db.close()


@app.post("/api/clean")
def clean_data(reset: bool = False):
    """Mark false positives (car washes, supermarkets, etc.) as excluded."""
    result = run_clean(reset=reset)
    return result


@app.get("/api/stats")
def get_stats():
    db = SessionLocal()
    try:
        valid_q = db.query(Laundry).filter(Laundry.excluded == False)
        total = valid_q.count()
        excluded_count = db.query(Laundry).filter(Laundry.excluded == True).count()
        by_region = (
            valid_q.with_entities(Laundry.region, func.count(Laundry.place_id))
            .filter(Laundry.region != "")
            .group_by(Laundry.region)
            .order_by(func.count(Laundry.place_id).desc())
            .all()
        )
        top = valid_q.order_by(Laundry.reviews_count.desc()).first()
        avg_rating = valid_q.with_entities(func.avg(Laundry.rating)).scalar()

        return {
            "total": total,
            "excluded": excluded_count,
            "avg_rating": round(avg_rating, 2) if avg_rating else None,
            "by_region": [{"region": r[0], "count": r[1]} for r in by_region],
            "top_laundry": {
                "name": top.name,
                "reviews_count": top.reviews_count,
                "city": top.city,
                "rating": top.rating,
            } if top else None,
        }
    finally:
        db.close()


@app.get("/api/filters")
def get_filters():
    db = SessionLocal()
    try:
        regions = db.query(Laundry.region).distinct().filter(Laundry.region != "").all()
        cities = db.query(Laundry.city).distinct().filter(Laundry.city != "").all()
        return {
            "regions": sorted([r[0] for r in regions if r[0]]),
            "cities": sorted([c[0] for c in cities if c[0]]),
        }
    finally:
        db.close()


@app.post("/api/scrape")
def trigger_scrape(background_tasks: BackgroundTasks):
    if _scrape_status["running"]:
        raise HTTPException(status_code=409, detail="Scraping already in progress")
    background_tasks.add_task(_run_scrape)
    return {"message": "Scraping started in background"}


@app.get("/api/scrape/status")
def scrape_status():
    return _scrape_status


@app.get("/api/debug/test-key")
def test_api_key():
    import os, requests
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("GOOGLE_PLACES_API_KEY")

    if not key or key == "COLOCA_AQUI_A_TUA_KEY":
        return {"ok": False, "error": "API key não configurada no .env"}

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    try:
        r = requests.get(url, params={"query": "lavandaria Lisboa", "key": key}, timeout=10)
        data = r.json()
        status = data.get("status")
        if status == "OK":
            return {"ok": True, "status": status, "results_count": len(data.get("results", []))}
        else:
            return {"ok": False, "status": status, "error": data.get("error_message", "Sem detalhes")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/export/csv")
def export_csv():
    db = SessionLocal()
    try:
        results = db.query(Laundry).order_by(Laundry.reviews_count.desc()).all()
        df = pd.DataFrame([_export_row(r) for r in results])
        stream = io.StringIO()
        df.to_csv(stream, index=False, encoding="utf-8-sig")
        stream.seek(0)
        return StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=lavanderias_portugal.csv"},
        )
    finally:
        db.close()


@app.get("/api/export/excel")
def export_excel():
    db = SessionLocal()
    try:
        results = db.query(Laundry).order_by(Laundry.reviews_count.desc()).all()
        df = pd.DataFrame([_export_row(r) for r in results])
        stream = io.BytesIO()
        with pd.ExcelWriter(stream, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Lavanderias")
        stream.seek(0)
        return StreamingResponse(
            iter([stream.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=lavanderias_portugal.xlsx"},
        )
    finally:
        db.close()


def _serialize(r: Laundry) -> dict:
    return {
        "place_id": r.place_id,
        "name": r.name,
        "address": r.address,
        "city": r.city,
        "region": r.region,
        "latitude": r.latitude,
        "longitude": r.longitude,
        "rating": r.rating,
        "reviews_count": r.reviews_count,
        "google_maps_url": r.google_maps_url,
        "phone": r.phone,
        "website": r.website,
    }


def _export_row(r: Laundry) -> dict:
    return {
        "Ranking": None,
        "Nome": r.name,
        "Cidade": r.city,
        "Região": r.region,
        "Morada": r.address,
        "Avaliação (estrelas)": r.rating,
        "Nº de Reviews": r.reviews_count,
        "Telefone": r.phone,
        "Website": r.website,
        "Link Google Maps": r.google_maps_url,
        "Latitude": r.latitude,
        "Longitude": r.longitude,
    }
