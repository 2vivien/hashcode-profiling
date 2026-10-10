from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse, Response

from orientation.api import templating

router = APIRouter(tags=["pages"])

_STATIC = Path(__file__).resolve().parents[1] / "static"

# page -> (fichier, clé de nav active, titre, description)
_PAGES: dict[str, tuple[str, str, str, str]] = {
    "home": (
        "home",
        "home",
        "hashcode.profiling — Comprendre avant d'orienter",
        "Moteur d'orientation : un profil multidimensionnel et évolutif, puis plusieurs directions à explorer — avec le pourquoi, l'incertitude et les compétences à renforcer.",
    ),
    "moteur": (
        "engine",
        "engine",
        "Le moteur — hashcode.profiling",
        "Le pipeline d'orientation étape par étape : observations, profil, candidats, matching, score, incertitude, diversification, explication.",
    ),
    "principes": (
        "principles",
        "principles",
        "Principes — hashcode.profiling",
        "Ce que le moteur fait, et ce qu'il ne fera jamais : ne pas imposer, expliquer, préserver l'incertitude, auditer l'équité.",
    ),
    "etat": (
        "etat",
        "state",
        "État réel — hashcode.profiling",
        "Code présent ≠ données présentes ≠ modèle entraîné ≠ modèle validé. L'état honnête du moteur.",
    ),
    "developers": (
        "developers",
        "developers",
        "Espace développeur — hashcode.profiling",
        "Statut système, paramètres de connexion, endpoints et extraits REST prêts à copier.",
    ),
}


def _render(key: str) -> HTMLResponse:
    page, active, title, description = _PAGES[key]
    return HTMLResponse(templating.render(page, active, title, description))


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> HTMLResponse:
    return _render("home")


@router.get("/moteur", response_class=HTMLResponse, include_in_schema=False)
def moteur() -> HTMLResponse:
    return _render("moteur")


@router.get("/principes", response_class=HTMLResponse, include_in_schema=False)
def principes() -> HTMLResponse:
    return _render("principes")


@router.get("/etat", response_class=HTMLResponse, include_in_schema=False)
def etat() -> HTMLResponse:
    return _render("etat")


@router.get("/developers", response_class=HTMLResponse, include_in_schema=False)
def developers() -> HTMLResponse:
    return _render("developers")


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(_STATIC / "favicon.ico", media_type="image/x-icon")


@router.get("/favicon.svg", include_in_schema=False)
def favicon_svg() -> FileResponse:
    return FileResponse(_STATIC / "favicon.svg", media_type="image/svg+xml")


@router.get("/apple-touch-icon.png", include_in_schema=False)
def apple_touch_icon() -> FileResponse:
    return FileResponse(_STATIC / "apple-touch-icon.png", media_type="image/png")


@router.get("/og.png", include_in_schema=False)
def og_image() -> FileResponse:
    return FileResponse(_STATIC / "og.png", media_type="image/png")


@router.get("/site.webmanifest", include_in_schema=False)
def webmanifest() -> Response:
    return Response(
        (_STATIC / "site.webmanifest").read_text(encoding="utf-8"),
        media_type="application/manifest+json",
    )
