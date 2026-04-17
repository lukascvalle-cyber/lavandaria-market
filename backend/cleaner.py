"""
Classifies scraped entries as excluded (false positives) or valid self-service laundromats.
Run standalone or called via API endpoint.
"""

from database import SessionLocal, Laundry

# These name patterns always indicate car wash businesses
CAR_WASH_PATTERNS = [
    "car wash", "carwash", "car-wash",
    "auto duche", "autoduche",
    "autojato", "auto jato",
    "elefante azul",
    "baleia verde",
    "imo car", "imo auto",
    "autowash", "auto wash",
    "jetwash", "jet wash",
    "ecocarwash", "eco car wash",
    "autolavagem", "auto lavagem",
    "lavagem auto", "lavagem de auto",
    "lavagem automóvel", "lavagem automovel",
    "lavagem de carro", "lavagem de veículo",
    "lavagem girassol",
    "bubble car",
    "spacewash", "spacwash",
    "aspiração automóvel", "aspiracao automovel",
    "limpeza de carro", "limpeza auto",
    "estofos",
    "planeta azul",
    "cadete wash",
    "prime wash",
    "wash4car",
    "lavagem rapida", "lava rápido auto",
    "atlantic car",
    "my carwash",
    "autojato",
    "cleanpark",
]

# These name patterns always indicate retail/supermarket/unrelated businesses
RETAIL_PATTERNS = [
    "continente",
    "pingo doce",
    "leroy merlin",
    "el corte inglés", "el corte ingles",
    "darty",
    "radio popular",
    "cidadela electrónica", "cidadela electronica",
    "electrodomésticos", "eletrodomésticos",
    "lidl",
    "intermarché", "intermarche",
    "aldi",
    "jumbo",
    "fnac",
    "almada forum",
    "shopping center", "centro comercial",
]

# Patterns that indicate other non-laundromat businesses
OTHER_PATTERNS = [
    "assistência técnica", "assistencia tecnica",
    "mavegon",
    "jotoparc",
    "costureira",
    "reparação", "reparacao",
]

# Strong indicators that a business IS a real self-service laundromat
# Used to rescue borderline names from the exclude list
LAUNDROMAT_INDICATORS = [
    "self service", "self-service",
    "lavandaria",
    "lavanderia",
    "coin laundry",
    "laundrette",
    "laundry",
    "lava e seca",
    "wash station", "washstation",
    "lavadouro",
]


def classify(name: str) -> tuple[bool, str | None]:
    """Returns (excluded, reason) for a given business name."""
    n = name.lower()

    # Check if it's clearly a laundromat first — this takes priority
    is_laundromat = any(kw in n for kw in LAUNDROMAT_INDICATORS)

    # Check exclusion categories
    if any(kw in n for kw in CAR_WASH_PATTERNS):
        if is_laundromat:
            return False, None  # e.g. "Wash4car Self-Service Laundry" would be rescued
        return True, "car_wash"

    if any(kw in n for kw in RETAIL_PATTERNS):
        if is_laundromat:
            return False, None
        return True, "retail"

    if any(kw in n for kw in OTHER_PATTERNS):
        if is_laundromat:
            return False, None
        return True, "other"

    return False, None


def run_clean(reset: bool = False) -> dict:
    """
    Classify all entries and mark false positives as excluded.
    If reset=True, clears all exclusions first (full re-run).
    Returns summary counts.
    """
    db = SessionLocal()
    try:
        if reset:
            db.query(Laundry).update({"excluded": False, "excluded_reason": None})
            db.commit()

        entries = db.query(Laundry).all()
        newly_excluded = 0
        newly_included = 0
        by_reason: dict[str, int] = {}

        for entry in entries:
            excluded, reason = classify(entry.name)
            if excluded != entry.excluded:
                entry.excluded = excluded
                entry.excluded_reason = reason
                if excluded:
                    newly_excluded += 1
                    by_reason[reason] = by_reason.get(reason, 0) + 1
                else:
                    newly_included += 1

        db.commit()

        total = db.query(Laundry).count()
        valid = db.query(Laundry).filter_by(excluded=False).count()
        excl = db.query(Laundry).filter_by(excluded=True).count()

        return {
            "total": total,
            "valid": valid,
            "excluded": excl,
            "newly_excluded": newly_excluded,
            "newly_included": newly_included,
            "by_reason": by_reason,
        }
    finally:
        db.close()


if __name__ == "__main__":
    result = run_clean(reset=True)
    print(result)
