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


import sys


def scope_to_env(scope, wsgi_input):
    """Convert ASGI scope to WSGI environ."""

    env = {
        # CGI variables
        'REQUEST_METHOD': scope['method'],
        'PATH_INFO': scope['path'],
        'QUERY_STRING': scope['query_string'],
        'SERVER_PROTOCOL': 'HTTP/' + scope['http_version'],
        # WSGI variables
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': scope.get('scheme', 'http'),
        'wsgi.input': wsgi_input,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': True,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    for header_name, header_value in scope['headers']:
        name = header_name.upper()
        value = header_value.decode('latin-1')
        if name == b'CONTENT-TYPE':
            env['CONTENT_TYPE'] = value
        elif name == b'CONTENT-LENGTH':
            env['CONTENT_LENGTH'] = value
        else:
            name = name.decode('latin-1').replace('-', '_')
            env[f'HTTP_{name}'] = value

    return env
