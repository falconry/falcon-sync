import falcon
import falcon.testing

from falcon_sync.wsgi import adapter
from falcon_sync.wsgi import request


def test_request_attributes():
    body = '{"color": "orange"}'
    req = falcon.testing.create_req(
        path='/items',
        method='POST',
        body=body,
        headers={
            'Content-Length': str(len(body)),
            'Content-Type': falcon.MEDIA_JSON,
        },
    )

    with adapter.Adapter() as sync_adapter:
        asgi_req = request.RequestProxy(req, sync_adapter)

        assert asgi_req.method == 'POST'
        assert asgi_req.path == '/items'
        assert asgi_req.content_type == 'application/json'
        assert asgi_req.content_length == 19

        media = sync_adapter.run_sync(asgi_req.get_media())
        assert media == {'color': 'orange'}
