import asyncio

import falcon.asgi

from falcon_sync.common import proxy
from falcon_sync.wsgi import protocol


class RequestProxy(falcon.asgi.Request, metaclass=proxy.ProxyMeta):
    _PROXY_INHERIT = frozenset({'get_media', 'media', 'stream'})

    _CHUNK_SIZE = 65536

    def __init__(self, req, adapter):
        self._request = req
        self._adapter = adapter

        self.scope = protocol.env_to_scope(req.env)

        self._disconnected = False
        self._first_event = None
        self._media = req._media
        self._media_error = req._media_error

    @property
    def options(self):
        return self._request.options

    async def _receive(self):
        if self._disconnected:
            return {'type': 'http.disconnect'}

        loop = asyncio.get_running_loop()
        body = await loop.run_in_executor(
            None, self._request.bounded_stream.read, self._CHUNK_SIZE
        )

        if len(body) == self._CHUNK_SIZE:
            return {
                'type': 'http.request',
                'body': body,
                'more_body': True,
            }

        self._disconnected = True
        return {
            'type': 'http.request',
            'body': body,
        }
