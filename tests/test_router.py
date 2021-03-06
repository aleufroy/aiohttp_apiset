import asyncio
from pathlib import Path

from aiohttp import web

from aiohttp_apiset import SwaggerRouter


def test_app(loop, swagger_router):
    app = web.Application(loop=loop)
    swagger_router.setup(app)


def test_search_dirs():
    d = Path(__file__).parent
    r = SwaggerRouter(d / 'data/include.yaml')
    r.add_search_dir(d)


def test_merge_spec():
    d = Path(__file__).parent
    r = SwaggerRouter(d / 'data/include.yaml')
    r.include('file.yaml', basePath='/inc')


def test_routes(swagger_router: SwaggerRouter):
    paths = [url for route, url in swagger_router._routes.values()]
    assert '/api/1/file/image' in paths


def test_route_include(swagger_router: SwaggerRouter):
    paths = [url for route, url in swagger_router._routes.values()]
    assert '/api/1/include2/inc/image' in paths


def test_route_swagger_include(swagger_router: SwaggerRouter):
    paths = next(iter(swagger_router._swagger_data.values()))['paths']
    assert '/include/image' in paths


def test_route_swagger_view(swagger_router: SwaggerRouter):
    paths = next(iter(swagger_router._swagger_data.values()))['paths']
    assert '/file/image' in paths


def test_handler(swagger_router: SwaggerRouter):
    paths = [(route.method, path)
             for route, path in swagger_router._routes.values()]
    assert ('GET', '/api/1/include/image') in paths


def test_definitions(swagger_router: SwaggerRouter):
    d = next(iter(swagger_router._swagger_data.values()))['definitions']
    assert 'File' in d
    assert 'Defi' in d


@asyncio.coroutine
def test_cbv_handler_get(client, swagger_router):
    url = swagger_router['file:simple:view'].url()
    res = yield from client.get(url)
    assert (yield from res.text()) == 'simple handler get'


@asyncio.coroutine
def test_cbv_handler_post(client, swagger_router):
    url = swagger_router['file:simple:view'].url()
    res = yield from client.post(url)
    assert (yield from res.text()) == 'simple handler post'


def test_override_basePath(loop):
    router = SwaggerRouter(search_dirs=['tests'])
    web.Application(router=router, loop=loop)
    prefix = '/override'
    router.include('data/root.yaml', basePath=prefix)
    paths = [
        url
        for route, url in router._routes.values()
        if url.startswith(prefix)
    ]
    assert prefix in router._swagger_data
    assert paths


def test_Path():
    base = Path(__file__).parent
    router = SwaggerRouter(
        search_dirs=[base],
        swagger_ui=False,
    )
    spec = base / 'data/root.yaml'
    router.include(spec)
    assert router._swagger_data
