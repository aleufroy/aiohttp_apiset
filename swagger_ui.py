#!/usr/bin/env python
""" Installer swagger-ui

Author: Alexander Malev
"""

import urllib.request
import tempfile
import zipfile
import shutil
import os
import sys

VERSION = os.environ.get('SWAGGER_UI_VERSION', '3.0.7')
PACKAGE = os.environ.get('PACKAGE', 'aiohttp_apiset')

URL = 'https://github.com/swagger-api/swagger-ui/archive/v{}.zip'
DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(DIR, PACKAGE, 'static', 'swagger-ui')
TEMPLATES_DIR = os.path.join(DIR, PACKAGE, 'templates', 'swagger-ui')
TEMPLATE_UI = os.path.join(TEMPLATES_DIR, 'index.html')

PREFIX = '{{static_prefix}}'
REPLACE_STRINGS = [
    ('http://petstore.swagger.io/v2/swagger.json', '{{url}}'),
    ('href="./', 'href="' + PREFIX + '/'),
    ('src="./', 'src="' + PREFIX + '/'),
]


def setup_ui():
    with urllib.request.urlopen(URL.format(VERSION)) as r, \
            tempfile.NamedTemporaryFile() as f:
        f.write(r.read())
        f.flush()
        with zipfile.ZipFile(f.name) as z, tempfile.TemporaryDirectory() as d:
            mask = 'swagger-ui-{}/dist'.format(VERSION)
            for member in z.namelist():
                if member.startswith(mask):
                    z.extract(member, path=d)
            shutil.move(os.path.join(d, mask), STATIC_DIR)

    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)

    with open(os.path.join(STATIC_DIR, 'index.html'), 'rt') as source:
        s = source.read()
    for target, source in REPLACE_STRINGS:
        s = s.replace(target, source)
    with open(TEMPLATE_UI, 'wt') as f:
        f.write(s)


def delete():
    shutil.rmtree(TEMPLATES_DIR)
    shutil.rmtree(STATIC_DIR)


if __name__ == '__main__':
    if 'delete' in sys.argv:
        delete()
    else:
        setup_ui()
