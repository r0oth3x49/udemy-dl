#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Author  : Nasir Khan (r0ot h3x49)
Github  : https://github.com/r0oth3x49
License : MIT


Copyright (c) 2020 Nasir Khan (r0ot h3x49)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH 
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

from ._compat import (
                sys,
                time,
                requests,
                HEADERS,
                LOGOUT_URL,
            )
from ._colorized import *


class Session(object):

    def __init__(self):
        self._headers = HEADERS
        self._session = requests.sessions.Session()

    def _set_auth_headers(self, access_token='', client_id=''):
        self._headers['Authorization'] = "Bearer {}".format(access_token)
        self._headers['X-Udemy-Authorization'] = "Bearer {}".format(access_token)

    def _get(self, url):
        session = self._session.get(url, headers=self._headers)
        if session.ok or session.status_code in [502, 503]:
            return session
        if not session.ok:
            if session.status_code == 403:
                msg = {'detail': 'You should use cookie base method to authenticate or try again in few minutes'}
            else:
                msg = {'detail': ''}
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Udemy Says : %s %s %s ...\n" % (session.status_code, session.reason, msg.get('detail', '')))
            time.sleep(0.8)
            sys.exit(0)

    def _post(self, url, data, redirect=True):
        session = self._session.post(url, data, headers=self._headers, allow_redirects=redirect)
        if session.ok:
            return session
        if not session.ok:
            if session.status_code == 403:
                msg = {'detail': 'You should use cookie base method to authenticate or try again in few minutes'}
            else:
                msg = {'detail': ''}
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Udemy Says : %s %s %s ...\n" % (session.status_code, session.reason, msg.get('detail', '')))
            sys.stdout.flush()
            time.sleep(0.8)
            sys.exit(0)

    def terminate(self):
        self._set_auth_headers()
        return
