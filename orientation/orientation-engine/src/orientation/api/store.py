"""Store partagé (data-service) — construction paresseuse et optionnelle."""

from __future__ import annotations

from functools import lru_cache

from orientation.config.settings import Settings
from orientation.infrastructure.persistence.orientation_store import OrientationStore


@lru_cache(maxsize=1)
def get_store() -> OrientationStore | None:
    """Renvoie ``None`` si aucune base n'est configurée ou si la persistance est off."""
    settings = Settings()
    if not settings.data_service_url or not settings.persist:
        return None
    return OrientationStore(settings.data_service_url)
