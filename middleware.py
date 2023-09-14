from starlette.requests import Request


class LowerCaseMiddleware:
    def __init__(self) -> None:
        self.DECODE_FORMAT = "latin-1"

    async def __call__(self, request: Request, call_next):
        # print(request.scope)
        path = request.scope["path"]
        if not path.startswith('/url'):
            # Makes query string lowercase
            raw = request.scope["query_string"].decode(self.DECODE_FORMAT).lower()
            request.scope["query_string"] = raw.encode(self.DECODE_FORMAT)
            # Makes path lowercase
            request.scope["path"] = path.lower()

        response = await call_next(request)
        return response
