"""Système de partials minimal (sans dépendance externe).

Réutilise des composants HTML indépendamment du transport :
- base.html      : gabarit commun (head, nav, footer, motion)
- partials/*.html : composants réutilisables (nav, footer, sections)
- pages/*.html    : contenu propre à chaque page

Syntaxe :
- ``{{include:nom}}``     insère ``partials/nom.html`` (récursif)
- ``{{active:cle}}``      marque le lien de nav actif (remplacé par `` active``)
- ``{{title}}``, ``{{description}}`` : injectés depuis la page
"""

import re
from pathlib import Path

_API = Path(__file__).resolve().parent
TEMPLATES = _API / "templates"
PARTIALS = TEMPLATES / "partials"
PAGES = TEMPLATES / "pages"

_INCLUDE = re.compile(r"\{\{include:([a-z0-9_]+)\}\}")
_ACTIVE = re.compile(r"\{\{active:([a-z0-9_]+)\}\}")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def expand(html: str) -> str:
    """Résout récursivement les ``{{include:...}}``."""
    for _ in range(10):
        new = _INCLUDE.sub(lambda m: _read(PARTIALS / f"{m.group(1)}.html"), html)
        if new == html:
            break
        html = new
    return html


def render(page: str, active: str, title: str, description: str) -> str:
    base = _read(TEMPLATES / "base.html")
    content = expand(_read(PAGES / f"{page}.html"))
    nav = _ACTIVE.sub(lambda m: " active" if m.group(1) == active else "", expand(_read(PARTIALS / "nav.html")))
    footer = expand(_read(PARTIALS / "footer.html"))
    html = base.replace("{{nav}}", nav).replace("{{content}}", content).replace("{{footer}}", footer)
    html = expand(html)
    return html.replace("{{title}}", title).replace("{{description}}", description)
