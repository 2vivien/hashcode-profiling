"""Cartographie : contours du monde et génération de SVG."""

from orientation.infrastructure.geography.world_map import (
    PALETTE,
    build_svg,
    load_coverage,
    load_occupations,
    load_world,
    match_occupations,
    project,
    render_country,
)

__all__ = [
    "PALETTE",
    "build_svg",
    "load_coverage",
    "load_occupations",
    "load_world",
    "match_occupations",
    "project",
    "render_country",
]
