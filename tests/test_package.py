import falcon_sync.asgi
import falcon_sync.wsgi


def test_package():
    assert falcon_sync.asgi is not None
    assert falcon_sync.wsgi is not None
