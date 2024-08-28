import falcon.asgi

from falcon_sync.common import proxy


class ResponseProxy(falcon.asgi.Response, metaclass=proxy.ProxyMeta):
    _PROXY_INHERIT = frozenset({})

    def __init__(self, resp, adapter):
        self._response = resp
        self._adapter = adapter

        # TODO(vytas): Safer to proxy these via private properties as well.
        self._media = resp._media
        self._media_rendered = resp._media_rendered

    @property
    def stream(self):
        return self._response.stream

    @stream.setter
    def stream(self, value):
        self._response.stream = self._adapter.wrap_async_gen(value)

    def set_stream(self, stream, content_length):
        self.stream = stream
        self.content_length = content_length

    async def render_body(self):
        return self._adapter.run_in_executor(self._response.render_body)
