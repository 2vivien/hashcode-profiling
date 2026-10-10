"""Durcissement HTTP : en-têtes de sécurité + clé d'API optionnelle.

La clé n'est exigée que si la variable d'environnement ``OTHELOO_API_KEY`` est
définie (non vide). En local/démo elle reste vide ; en production on l'active
et les consommateurs (Otheloo, outils) envoient l'en-tête ``X-API-Key``.
"""

from __future__ import annotations

import hmac
import os

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

_PROTECTED_PREFIX = "/v1/"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        return response


class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        expected = os.environ.get("OTHELOO_API_KEY", "")
        if expected and request.url.path.startswith(_PROTECTED_PREFIX):
            provided = request.headers.get("x-api-key", "")
            if not hmac.compare_digest(provided, expected):
                return JSONResponse({"detail": "invalid or missing API key"}, status_code=401)
        return await call_next(request)
