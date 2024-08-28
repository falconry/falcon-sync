import falcon
import falcon.testing

from falcon_sync.wsgi.adapter import Adapter


class WordsResource:
    def __init__(self):
        self._data = {}

    async def on_put(self, req, resp, itemid):
        data = await req.stream.read()
        self._data[itemid] = data.strip().decode()
        resp.status = falcon.HTTP_NO_CONTENT

    async def on_get(self, req, resp, itemid):
        async def word_generator():
            for word in words:
                yield word.encode() + b' '

        sentence = self._data.get(itemid)
        if sentence is None:
            raise falcon.HTTPNotFound
        words = sentence.split()
        resp.content_length = sum(len(word) + 1 for word in words)
        resp.content_type = falcon.MEDIA_TEXT
        resp.stream = word_generator()


def test_async_generator():
    pangram = 'The quick brown fox jumps over the lazy dog'
    resource = WordsResource()

    app = falcon.App()

    with Adapter() as adapter:
        wrapped = adapter.wrap_resource(resource)
        app.add_route('/words/{itemid}', wrapped)

        result1 = falcon.testing.simulate_put(
            app, '/words/s1337', body=pangram
        )
        assert result1.status_code == 204

        result2 = falcon.testing.simulate_get(app, '/words/s_1337')
        assert result2.status_code == 404

        result3 = falcon.testing.simulate_get(app, '/words/s1337')
        assert result3.status_code == 200
        assert result3.text == pangram + ' '
