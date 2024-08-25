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


def env_to_scope(env, state=None):
    """Convert WSGI environ to ASGI scope."""

    # PERF(vytas): Content-Length should normally exist.
    try:
        headers = [[b'content-length', env['CONTENT_LENGTH'].encode()]]
    except KeyError:
        headers = []

    if 'CONTENT_TYPE' in env:
        headers.append(
            [b'content-type', env['CONTENT_TYPE'].encode('latin-1')]
        )

    for name, value in env.items():
        if name.startswith('HTTP_'):
            headers.append(
                [name[5:].replace('_', '-').encode(), value.encode('latin-1')]
            )

    scope = {
        'type': 'http',
        'asgi': {
            'version': '3.0',
            'spec_version': '2.4',
        },
        'http_version': env['SERVER_PROTOCOL'].split('/')[-1],
        'method': env['REQUEST_METHOD'],
        # scheme is set below
        'path': env['PATH_INFO'] or '/',
        # query_string is set below
        # root_path is set below
        'headers': headers,
        # client is set below
        # server is set below
        # state is set below
    }

    # PERF(vytas): We expect wsgi.url_scheme to exist.
    try:
        scope['scheme'] = env['wsgi.url_scheme']
    except KeyError:
        pass

    # PERF(vytas): We expect query string to exist.
    try:
        scope['query_string'] = env['QUERY_STRING']
    except KeyError:
        scope['query_string'] = ''

    # PERF(vytas): Most WSGI servers set SCRIPT_NAME even if empty.
    try:
        scope['root_path'] = env['SCRIPT_NAME']
    except KeyError:
        pass

    # NOTE(vytas): These usually exist, and it is easier to handle two
    #   exceptions at once.
    try:
        scope['client'] = [env['REMOTE_ADDR'], env['REMOTE_PORT']]
    except KeyError:
        pass

    # NOTE(vytas): These usually exist, and it is easier to handle two
    #   exceptions at once.
    try:
        scope['server'] = [env['SERVER_NAME'], env['SERVER_PORT']]
    except KeyError:
        pass

    if state is not None:
        scope['state'] = state

    return scope
