from fastapi import Request


def get_request_id(request: Request) -> str:
    return request.headers.get("x-request-id", "generated-by-api")
