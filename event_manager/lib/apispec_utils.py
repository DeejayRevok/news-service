from aiohttp import web
from pathlib import Path

import aiohttp_apispec
from jinja2 import Template


def setup_aiohttp_apispec_mod(
    app: web.Application,
    *,
    title: str = "API documentation",
    version: str = "0.0.1",
    url: str = "/api/docs/swagger.json",
    request_data_name: str = "data",
    swagger_path: str = None,
    static_path: str = '/static/swagger',
    error_callback=None,
    in_place: bool = False,
    prefix: str = '',
    static_base_url: str = None,
    **kwargs
) -> None:
    AiohttpApiSpecMod(
        url,
        app,
        request_data_name,
        title=title,
        version=version,
        swagger_path=swagger_path,
        static_path=static_path,
        error_callback=error_callback,
        in_place=in_place,
        prefix=prefix,
        static_base_url=static_base_url,
        **kwargs
    )


class AiohttpApiSpecMod(aiohttp_apispec.AiohttpApiSpec):

    def __init__(self, url="/api/docs/swagger.json", app=None, request_data_name="data", swagger_path=None,
                 static_path='/static/swagger', error_callback=None, in_place=False, prefix='', static_base_url=None,
                 **kwargs):
        self.static_base_url = static_base_url
        super().__init__(url, app, request_data_name, swagger_path, static_path, error_callback, in_place, prefix,
                         **kwargs)

    def _add_swagger_web_page(self, app: web.Application, static_path: str, view_path: str):
        static_files = Path(aiohttp_apispec.__file__).parent / "static"
        app.router.add_static(static_path, static_files)

        with open(str(static_files / "index.html")) as swg_tmp:
            if self.static_base_url is not None:
                tmp = Template(swg_tmp.read()).render(path=self.url, static=self.static_base_url+static_path)
            else:
                tmp = Template(swg_tmp.read()).render(path=self.url, static=static_path)

        async def swagger_view(_):
            return web.Response(text=tmp, content_type="text/html")

        app.router.add_route("GET", view_path, swagger_view, name="swagger.docs")