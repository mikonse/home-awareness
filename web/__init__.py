import asyncio
from threading import Thread

from aiohttp import web
from aiohttp.abc import Request, StreamResponse

from config import config
import tracking

routes = web.RouteTableDef()


@routes.get('/api/tracking/')
async def api_tracking_list():
    return tracking.get_current_users()


@routes.get('/api/config')
async def api_config(request: Request) -> StreamResponse:
    try:
        data = request.json()
    except:
        raise web.HTTPBadRequest()
    config.update(data, full=True)

    return web.json_response(config.serialize_json(full=True))


@routes.post('/api/config')
async def api_config_post(request: Request) -> StreamResponse:
    return web.json_response(config.serialize_json(full=True))


def _serve(loop: asyncio.AbstractEventLoop, shutdown_signal: asyncio.Event, host: str, port: int) -> None:
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    asyncio.set_event_loop(loop)
    asyncio.set_event_loop(loop)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, host, port)
    loop.run_until_complete(site.start())
    loop.run_until_complete(shutdown_signal.wait())


async def main(shutdown_signal: asyncio.Event):
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    await shutdown_signal.wait()


if __name__ == '__main__':
    asyncio.run(main())
