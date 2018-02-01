#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 The Wenchen Li. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""
simple spacy tagger services

"""
from argparse import ArgumentParser
from cgi import FieldStorage
from os.path import dirname, join as path_join
from spacy_offline_tag import tag_to_json

import spacy

try:
    from json import dumps
except ImportError:
    # likely old Python; try to fall back on ujson in brat distrib
    from sys import path as sys_path
    sys_path.append(path_join(dirname(__file__), '../../server/lib/ujson'))
    from ujson import dumps

from sys import stderr
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

### Constants
ARGPARSER = ArgumentParser(description='XXX')#XXX:
ARGPARSER.add_argument('-p', '--port', type=int, default=47111,
        help='port to run the HTTP service on (default: 47111)')
TAGGER = None
MODEL = 'en'

class spacyTaggerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print >> stderr, 'Received request'
        field_storage = FieldStorage(
                headers=self.headers,
                environ={
                    'REQUEST_METHOD':'POST',
                    'CONTENT_TYPE':self.headers['Content-Type'],
                    },
                fp=self.rfile)

        global TAGGER
        json_dic = tag_to_json(TAGGER,field_storage.value.decode('utf8','ignore'))

        # Write the response
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

        self.wfile.write(dumps(json_dic))
        print >> stderr, ('Generated %d annotations' % len(json_dic))

    def log_message(self, format, *args):
        return # Too much noise from the default implementation

def main(args):
    argp = ARGPARSER.parse_args(args[1:])

    print >> stderr, "WARNING: Don't use this in a production environment!"

    print >> stderr, 'Starting spaCy',
    global TAGGER
    TAGGER = spacy.load(MODEL)
    print >> stderr, 'Done!'

    server_class = HTTPServer
    httpd = server_class(('localhost', argp.port), spacyTaggerHandler)
    print >> stderr, 'spacy tagger service started'
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print >> stderr, 'spacy tagger service stopped'

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
