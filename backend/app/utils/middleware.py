from fastapi import Request
from uuid import uuid4

class RequestIdMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
