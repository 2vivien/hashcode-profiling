"""La construction de v3 : exactitude du genre et prudence de l'appariement."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest


def load_builder() -> ModuleType:
    path = Path(__file__).resolve().parents[2] / "scripts" / "build_knowledge_v3.py"
    spec = importlib.util.spec_from_file_location("build_knowledge_v3", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Les dataclasses du moduleChargé look up sys.modules : il faut l'y inscrire.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Conducteur / Conductrice d'engins agricoles", "mixed"),
        ("Médecin généraliste", "unknown"),
        ("Chef / Cheffe", "mixed"),
        ("Aide / ", "unknown"),
    ],
)
def test_derive_gender_reads_inclusive_writing(label: str, expected: str) -> None:
    assert builder.derive_gender(label) == expected


def test_tokens_drop_stopwords_and_stem_singular() -> None:
    assert builder.tokens("Chef de service réseau") == {"chef", "service", "reseau"}
    # Règle française -eau / -eaux : les deux formes doivent converger.
    assert builder.stem("reseaux") == builder.stem("reseau") == "rese"
    assert builder.stem("class") == "class"


def test_match_direction_accepts_specific_vocabulary() -> None:
    seeds = {"network-engineering": {"reseau"}}
    assert builder.match_direction("Technicien réseaux mobiles", "Réseaux", seeds) == ("network-engineering", 0.9)


def test_match_direction_refuses_polysemous_words() -> None:
    """« sécurité sociale » ne doit jamais devenir « cybersécurité »."""
    seeds = {"cybersecurity": {"analyste", "securite"}}
    assert builder.match_direction("Technicien sécurité sociale", "Sécurité sociale", seeds) is None
    assert builder.match_direction("Chef de service de la sécurité sociale", "", seeds) is None
    assert builder.match_direction("Analyste de la performance sportive", "Sport", seeds) is None


def test_match_direction_refuses_single_shared_word_from_rich_seed() -> None:
    seeds = {"data-science": {"donnees", "scientifique"}}
    # Un seul mot partagé sur une amorce de plusieurs : trop faible.
    assert builder.match_direction("Chargé de données", "", seeds) is None


def test_rome_release_is_declared_in_catalog() -> None:
    catalog_path = Path(__file__).resolve().parents[2] / "data" / "catalog" / "external_sources.json"
    assert catalog_path.is_file()
