import falcon
import falcon.testing

from falcon_sync.wsgi.adapter import Adapter


class MediaMirror:
    async def on_post(self, req, resp):
        resp.media = await req.get_media()


def test_wrapped_media():
    resource = MediaMirror()

    app = falcon.App()

    with Adapter() as adapter:
        wrapped = adapter.wrap_resource(resource)
        app.add_route('/media', wrapped)

        data = {'color': 'orange', 'id': 1337}
        result = falcon.testing.simulate_post(app, '/media', json=data)
        assert result.status_code == 200
        assert result.json == data
