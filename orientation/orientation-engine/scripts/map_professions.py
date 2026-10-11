#!/usr/bin/env python3
"""Ligne de commande : exporte une carte du monde des données du moteur.

La logique vit dans `orientation.infrastructure.geography.world_map` — c'est
elle que l'API utilise aussi. Ce fichier n'est qu'un wrapper, pour qu'il n'y ait
qu'une seule implémentation à maintenir.

Usage :
    python3 scripts/map_professions.py
    python3 scripts/map_professions.py --profession géologue
    python3 scripts/map_professions.py --output /tmp/carte.svg
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from orientation.infrastructure.geography.world_map import (
    PALETTE,
    build_svg,
    load_coverage,
    load_occupations,
    load_world,
    match_occupations,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--profession", help="Filtre sur un métier (ex. géologue, ingénieur).")
    parser.add_argument("--output", type=Path, help="Fichier SVG de sortie (défaut : stdout).")
    parser.add_argument("--title", help="Titre de la carte.")
    args = parser.parse_args()

    try:
        countries = load_world()
    except FileNotFoundError as error:
        print(f"[map] {error}", file=sys.stderr)
        print("[map] Lancez : python3 scripts/fetch_world_map.py", file=sys.stderr)
        return 1

    coverage = load_coverage()
    occupations = load_occupations()
    known = {country["iso"] for country in countries} | {country["iso2"] for country in countries}
    covered = {code: len(occupations) for code in (coverage.get("country_names") or {}) if code in known}

    subtitle = "Répartition réelle des métiers, lue dans la base"
    title = args.title or "Couverture géographique de la connaissance"
    if args.profession:
        matches = match_occupations(args.profession)
        subtitle = f"{len(matches)} fiche(s) métier pour « {args.profession} » · carte de couverture"
        title = args.title or f"Métiers « {args.profession} »"
        print(f"[map] {len(matches)} fiche(s) pour « {args.profession} » :", file=sys.stderr)
        for occupation in matches[:12]:
            print(f"        - {occupation.get('title')}", file=sys.stderr)
        if len(matches) > 12:
            print(f"        … et {len(matches) - 12} autres", file=sys.stderr)

    svg = build_svg(
        countries,
        covered,
        title,
        subtitle,
        [(PALETTE["covered"], "Données réelles chargées"), (PALETTE["land"], "Aucune donnée")],
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(svg, encoding="utf-8")
        print(f"[map] écrit dans {args.output} ({len(svg)} octets)", file=sys.stderr)
    else:
        print(svg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
