import io
import json

from orientation.infrastructure.knowledge import remote as remote_module
from orientation.infrastructure.knowledge.remote import RemoteKnowledge

_SAMPLE = [
    {
        "id": "software-engineering",
        "version": "v1",
        "data": {
            "direction_id": "software-engineering",
            "canonical_name": "Ingénierie logicielle",
            "taxonomy": "technology",
            "interests": {"investigative": 0.8},
        },
    }
]


class _FakeResponse(io.BytesIO):
    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: object) -> bool:
        return False


def test_returns_none_when_unreachable(monkeypatch) -> None:
    def boom(*args: object, **kwargs: object) -> None:
        raise OSError("service down")

    monkeypatch.setattr(remote_module.request, "urlopen", boom)
    assert RemoteKnowledge("http://data", "v1").directions() is None


def test_parses_directions(monkeypatch) -> None:
    monkeypatch.setattr(
        remote_module.request,
        "urlopen",
        lambda *a, **k: _FakeResponse(json.dumps(_SAMPLE).encode()),
    )
    directions = RemoteKnowledge("http://data", "v1").directions()
    assert directions is not None
    assert directions[0].direction_id == "software-engineering"


def test_cache_avoids_second_call(monkeypatch) -> None:
    calls = {"n": 0}

    def ok(*args: object, **kwargs: object) -> _FakeResponse:
        calls["n"] += 1
        return _FakeResponse(json.dumps(_SAMPLE).encode())

    monkeypatch.setattr(remote_module.request, "urlopen", ok)
    client = RemoteKnowledge("http://data", "v1", ttl=60.0)
    client.directions()
    client.directions()
    assert calls["n"] == 1


def test_invalid_payload_returns_none(monkeypatch) -> None:
    monkeypatch.setattr(
        remote_module.request,
        "urlopen",
        lambda *a, **k: _FakeResponse(b"not json"),
    )
    assert RemoteKnowledge("http://data", "v1").directions() is None


def test_empty_directions_returns_none(monkeypatch) -> None:
    monkeypatch.setattr(
        remote_module.request,
        "urlopen",
        lambda *a, **k: _FakeResponse(b"[]"),
    )
    assert RemoteKnowledge("http://data", "v1").directions() is None
