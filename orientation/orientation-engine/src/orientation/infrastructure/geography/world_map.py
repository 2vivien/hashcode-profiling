"""Génération de cartes du monde en SVG, sans dépendance externe.

Deux consommateurs, une seule implémentation :

- l'API (`GET /v1/orientation/atlas/map.svg`), qui injecte la carte dans l'interface ;
- la ligne de commande (`scripts/map_professions.py`), pour exporter une carte
  d'un métier précis.

Le tracé est fait en Python plutôt qu'avec une bibliothèque JavaScript : pas de
dépendance côté navigateur, rendu net à toute taille, et un fichier que l'on peut
différer enougit — ce qu'une carte dessinée en JS ne permet pas.
"""

import json
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "data" / "raw" / "geography"
WORLD = RAW / "ne_110m_admin_0_countries.geojson"
KNOWLEDGE = ROOT / "data" / "knowledge"
COVERAGE = ROOT / "data" / "catalog" / "coverage.json"

WIDTH, HEIGHT = 1000, 520
LONGITUDE_RANGE = (-180.0, 180.0)
LATITUDE_RANGE = (83.0, -56.0)

# ISO_A3 vaut parfois -99 dans Natural Earth (petits territoires). On garde
# ADMIN comme repli plutôt que d'exclure ces pays de la carte.
ISO_FALLBACK = {
    "France": "FRA",
    "Norway": "NOR",
    "Somaliland": "SOM",
    "Kosovo": "XKX",
    "N. Cyprus": "CYP",
    "Cyprus": "CYP",
}

PALETTE = {
    "land": "#161c28",
    "border": "#232b3a",
    "covered": "#2fbf71",
    "matched": "#22d3ee",
    "ocean": "#07090f",
    "text": "#eef1f6",
    "muted": "#9aa3b2",
}


def normalize(text: str) -> str:
    """Minuscules sans accents : « Ingénieur » == « ingenieur »."""
    decomposed = unicodedata.normalize("NFKD", text or "")
    return "".join(char for char in decomposed if not unicodedata.combining(char)).lower()


def _clean_iso(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text in {"", "-99"} else text


def project(lon: float, lat: float) -> tuple[float, float]:
    """Équirectangulaire : lon/lat → pixels.

    Les coordonnées sont bornées : l'Antarctique dépasse -56° de latitude et
    dessinerait des points hors du cadre, ce qui élargit la boîte à l'impression
    sans rien apporter à la lecture.
    """
    left, right = LONGITUDE_RANGE
    top, bottom = LATITUDE_RANGE
    clamped_lon = min(max(lon, left), right)
    clamped_lat = min(max(lat, bottom), top)
    x = (clamped_lon - left) / (right - left) * WIDTH
    y = (top - clamped_lat) / (top - bottom) * HEIGHT
    return x, y


def load_world() -> list[dict[str, Any]]:
    if not WORLD.is_file():
        raise FileNotFoundError(f"contours du monde absents ({WORLD}). Lancez : python3 scripts/fetch_world_map.py")
    payload = json.loads(WORLD.read_text(encoding="utf-8"))
    countries: list[dict[str, Any]] = []
    for feature in payload.get("features", []):
        props = feature.get("properties") or {}
        name = props.get("ADMIN") or props.get("NAME") or ""
        # Natural Earth met -99 sur certains territoires ; le suffixe _EH est la
        # valeur corrigée. On expose les deux codes : la couverture est écrite
        # en ISO 3166-1 alpha-2 (« FR »), Natural Earth est en alpha-3 (« FRA »).
        iso3 = _clean_iso(props.get("ISO_A3_EH") or props.get("ISO_A3"))
        iso2 = _clean_iso(props.get("ISO_A2_EH") or props.get("ISO_A2"))
        if iso3 in {"", "-99"}:
            iso3 = ISO_FALLBACK.get(name, name[:3].upper())
        countries.append(
            {
                "iso": iso3,
                "iso2": iso2 or iso3[:2],
                "name": name,
                "name_fr": props.get("NAME_FR") or name,
                "continent": props.get("CONTINENT") or "",
                "geometry": feature.get("geometry") or {},
            }
        )
    return countries


def rings_of(geometry: dict[str, Any]) -> list[list[list[float]]]:
    """Aplatit Polygon/MultiPolygon en liste de anneaux (lon, lat)."""
    if not geometry:
        return []
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates") or []
    if kind == "Polygon":
        return [list(ring) for ring in coordinates]
    if kind == "MultiPolygon":
        return [list(ring) for polygon in coordinates for ring in polygon]
    return []


def render_country(country: dict[str, Any], fill: str, stroke: str) -> list[str]:
    paths: list[str] = []
    for ring in rings_of(country["geometry"]):
        if len(ring) < 3:
            continue
        commands: list[str] = []
        for index, point in enumerate(ring):
            lon, lat = float(point[0]), float(point[1])
            x, y = project(lon, lat)
            commands.append(f"{'M' if index == 0 else 'L'}{x:.1f},{y:.1f}")
        commands.append("Z")
        paths.append(f'<path d="{"".join(commands)}" fill="{fill}" stroke="{stroke}" stroke-width="0.4"/>')
    return paths


def knowledge_version() -> str:
    if COVERAGE.is_file():
        try:
            return str(json.loads(COVERAGE.read_text(encoding="utf-8")).get("version") or "v3")
        except json.JSONDecodeError:
            return "v3"
    return "v3"


def load_occupations() -> list[dict[str, Any]]:
    version = knowledge_version()
    path = KNOWLEDGE / version / "occupations.json"
    if not path.is_file():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return list(payload) if isinstance(payload, list) else []


def load_coverage() -> dict[str, Any]:
    if not COVERAGE.is_file():
        return {}
    try:
        payload: dict[str, Any] = json.loads(COVERAGE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload


def match_occupations(profession: str) -> list[dict[str, Any]]:
    """Fiches métier dont le libellé contient le métier cherché."""
    needle = normalize(profession).strip()
    if not needle:
        return []
    results: list[dict[str, Any]] = []
    for occupation in load_occupations():
        haystack = normalize(" ".join([str(occupation.get("title") or ""), str(occupation.get("domaine") or "")]))
        if needle in haystack:
            results.append(occupation)
    results.sort(key=lambda item: str(item.get("title") or ""))
    return results


def build_svg(
    countries: list[dict[str, Any]],
    covered: dict[str, int],
    title: str,
    subtitle: str,
    legend: list[tuple[str, str]],
) -> str:
    body: list[str] = []
    body.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{PALETTE["ocean"]}"/>')

    for country in countries:
        # La couverture est en ISO alpha-2, Natural Earth en alpha-3 : on
        # accepte les deux, sinon aucun pays n'apparaîtrait comme couvert.
        count = covered.get(country["iso"], 0) or covered.get(country["iso2"], 0)
        fill = PALETTE["covered"] if count else PALETTE["land"]
        stroke = PALETTE["matched"] if count else PALETTE["border"]
        paths = render_country(country, fill, stroke)
        if paths and count:
            label = f"{country['name_fr']} — {count:,} option(s)".replace(",", " ")
            body.append(f'<g class="c" data-name="{country["name_fr"]}"><title>{label}</title>{"".join(paths)}</g>')
        else:
            body.append(f'<g class="c"><title>{country["name_fr"]} — non couvert</title>{"".join(paths)}</g>')

    legend_svg: list[str] = []
    for index, (color, label) in enumerate(legend):
        x = 20 + index * 210
        legend_svg.append(f'<rect x="{x}" y="{HEIGHT - 26}" width="11" height="11" rx="2.5" fill="{color}"/>')
        legend_svg.append(f'<text x="{x + 17}" y="{HEIGHT - 17}" fill="{PALETTE["muted"]}" font-size="12">{label}</text>')

    covered_names = ", ".join(sorted(c["name_fr"] for c in countries if covered.get(c["iso"], 0) or covered.get(c["iso2"], 0))) or "aucun pays"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="{title}">
<style>
  text{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif}}
  .c{{cursor:default}}
  .c:hover path{{stroke:#eef1f6;stroke-width:1.1}}
</style>
{"".join(body)}
<text x="20" y="30" fill="{PALETTE["text"]}" font-size="19" font-weight="600">{title}</text>
<text x="20" y="50" fill="{PALETTE["muted"]}" font-size="12.5">{subtitle}</text>
<text x="20" y="68" fill="{PALETTE["muted"]}" font-size="12.5">Pays couverts : {covered_names}</text>
{"".join(legend_svg)}
<text x="20" y="{HEIGHT - 46}" fill="{PALETTE["muted"]}" font-size="10.5">Contours : Natural Earth 110 m (domaine public) · projection équirectangulaire</text>
</svg>"""
