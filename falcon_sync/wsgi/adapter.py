# Copyright 2024 by Vytautas Liuolia.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import functools
import inspect
import threading


class Adapter:
    def __init__(self):
        self._loop = None
        self._thread = None

    def start(self):
        def run_in_thread(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=run_in_thread, args=(self._loop,), daemon=True
        )
        self._thread.start()

    def join(self):
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()

    def __enter__(self):
        if self._loop is None:
            self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.join()

    def _call(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    def wrap_falcon_func(self, func):
        @functools.wraps(func)
        def sync_wrapper(req, resp, *args, **kwargs):
            coro = func(req, resp, *args, **kwargs)
            return self._call(coro)

        return sync_wrapper

    def wrap_resource(self, resource):
        class Wrapper:
            pass

        wrapped = Wrapper()

        for responder_name, responder in inspect.getmembers(
            resource, inspect.ismethod
        ):
            # TODO(vytas): Use a more advanced logic like in falcon.hooks.
            if responder_name.startswith('on_'):
                setattr(
                    wrapped, responder_name, self.wrap_falcon_func(responder)
                )

        return wrapped
