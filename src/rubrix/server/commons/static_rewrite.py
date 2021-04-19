from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.types import Scope


class RewriteStaticFiles(StaticFiles):
    """Simple server rewrite implementation for SPI apps"""

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        if self.html and response.status_code == 404:
            response = await super().get_response(path="", scope=scope)
        return response
