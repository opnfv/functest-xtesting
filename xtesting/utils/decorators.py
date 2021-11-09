#!/usr/bin/env python

# Copyright (c) 2017 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import errno
import functools
import os
from urllib.parse import urlparse

import mock
import requests.sessions


def can_dump_request_to_file(method):

    def dump_preparedrequest(request, **kwargs):
        # pylint: disable=unused-argument
        parseresult = urlparse(request.url)
        if parseresult.scheme == "file":
            try:
                dirname = os.path.dirname(parseresult.path)
                os.makedirs(dirname)
            except OSError as ex:
                if ex.errno != errno.EEXIST:
                    raise
            with open(parseresult.path, 'a', encoding='utf-8') as dumpfile:
                headers = ""
                for key in request.headers:
                    headers += key + " " + request.headers[key] + "\n"
                message = (
                    f"{request.method} {request.url}"
                    f"\n{headers}\n{request.body}\n\n\n")
                dumpfile.write(message)
        return mock.Mock()

    def patch_request(method, url, **kwargs):
        with requests.sessions.Session() as session:
            parseresult = urlparse(url)
            if parseresult.scheme == "file":
                with mock.patch.object(session, 'send',
                                       side_effect=dump_preparedrequest):
                    return session.request(method=method, url=url, **kwargs)
            else:
                return session.request(method=method, url=url, **kwargs)

    @functools.wraps(method)
    def hook(*args, **kwargs):
        with mock.patch('requests.api.request', side_effect=patch_request):
            return method(*args, **kwargs)

    return hook
