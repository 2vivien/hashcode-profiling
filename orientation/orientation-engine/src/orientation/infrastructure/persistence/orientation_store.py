"""Persistance best-effort vers le data-service (source de vérité).

Aucune écriture ne doit faire échouer une recommandation : en cas d'indisponibilité
du data-service, la méthode renvoie ``False`` et le moteur continue.
"""

from __future__ import annotations

import json
from typing import Any
from urllib import error, request

from orientation.contracts.profile import StudentProfile
from orientation.contracts.recommendation import Recommendation


def profile_payload(profile: StudentProfile) -> dict[str, Any]:
    return {
        "studentRef": profile.student_id,
        "profileVersion": profile.profile_version,
        "assessmentConfidence": profile.assessment_confidence,
        "dimensions": {
            "interests": profile.interests,
            "abilities": profile.abilities,
            "values": profile.values,
            "subjects": profile.subjects,
            "self_efficacy": profile.self_efficacy,
            "adaptability": profile.adaptability,
            "environment": profile.environment,
            "trajectory": profile.trajectory,
            "skills": {skill.skill_id: skill.level for skill in profile.skills},
        },
        "constraints": dict(profile.constraints),
    }


def recommendation_payload(
    profile: StudentProfile, recommendation: Recommendation
) -> dict[str, Any]:
    return {
        "id": recommendation.recommendation_id,
        "studentRef": profile.student_id,
        "profileVersion": recommendation.profile_version,
        "modelVersion": recommendation.model_version,
        "knowledgeVersion": recommendation.knowledge_version,
        "audit": recommendation.audit.model_dump(mode="json"),
        "items": [
            {
                "directionId": item.direction_id,
                "rank": index,
                "score": item.score,
                "confidence": item.confidence,
                "uncertainty": item.uncertainty,
                "payload": item.model_dump(mode="json"),
            }
            for index, item in enumerate(recommendation.candidates)
        ],
    }


class OrientationStore:
    def __init__(self, base_url: str, timeout: float = 2.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _post(self, path: str, payload: dict[str, Any]) -> bool:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:  # nosec B310
                return 200 <= int(response.status) < 300
        except (error.URLError, TimeoutError, OSError, ValueError):
            return False

    def _get(self, path: str) -> dict[str, Any] | None:
        try:
            with request.urlopen(f"{self.base_url}{path}", timeout=self.timeout) as resp:  # nosec B310
                payload = json.loads(resp.read().decode("utf-8"))
        except (error.URLError, TimeoutError, OSError, ValueError):
            return None
        return payload if isinstance(payload, dict) else None

    def save_profile(self, profile: StudentProfile) -> bool:
        return self._post("/profiles", profile_payload(profile))

    def save_recommendation(self, profile: StudentProfile, recommendation: Recommendation) -> bool:
        return self._post("/recommendations", recommendation_payload(profile, recommendation))

    def save_feedback(self, event: dict[str, Any]) -> bool:
        return self._post("/feedback", event)

    def get_profile(self, student_ref: str) -> dict[str, Any] | None:
        return self._get(f"/profiles/{student_ref}")
