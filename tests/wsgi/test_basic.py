import asyncio

import falcon
import falcon.testing

from falcon_sync.wsgi.adapter import Adapter


class AsyncResource:
    async def on_get(self, req, resp, itemid):
        result = await asyncio.sleep(0.001, result='pass')
        resp.media = {'itemid': itemid, 'result': result}

    on_head = on_get


def test_wrap_resource():
    resource = AsyncResource()

    app = falcon.App()

    with Adapter() as adapter:
        wrapped = adapter.wrap_resource(resource)
        app.add_route('/test/{itemid}', wrapped)

        result = falcon.testing.simulate_get(app, '/test/1337')
        assert result.status_code == 200
        assert result.json == {'itemid': '1337', 'result': 'pass'}

        result = falcon.testing.simulate_head(app, '/test/1337')
        assert result.status_code == 200
