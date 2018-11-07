#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

Author  : Nasir Khan (r0ot h3x49)
Github  : https://github.com/r0oth3x49
License : MIT


Copyright (c) 2018 Nasir Khan (r0ot h3x49)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH 
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from pprint import pprint
from ._session import Session
from ._compat import (
        sys,
        time,
        conn_error,
        LOGIN_POPUP,
        LOGIN_URL,
        )
from ._utils import (
        parse_json,
        js_to_json,
        search_regex,
        hidden_inputs,
        unescapeHTML,
        )
from ._colorized import *

class UdemyAuth(object):

    def __init__(self, username='', password=''):
        self.username = username
        self.password = password
        self._session = Session()

    def _form_hidden_input(self, form_id):
        try:
            webpage = self._session._get(LOGIN_POPUP).text
        except conn_error as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
            time.sleep(0.8)
            sys.exit(0)
        else:
            login_form = hidden_inputs(
                            search_regex(
                                r'(?is)<form[^>]+?id=(["\'])%s\1[^>]*>(?P<form>.+?)</form>' % form_id,
                                webpage,
                                '%s form' % form_id,
                                group='form'
                                )
                            )
            login_form.update({
                'email'     : self.username,
                'password'  : self.password,
                })
            return login_form

    def authenticate(self, access_token='', client_id=''):
        if not access_token and not client_id:
            form = self._form_hidden_input('login-form')
            auth_response = self._session._post(LOGIN_URL, data=form)
            auth_cookies = auth_response.cookies

            access_token = auth_cookies.get('access_token') or None
            client_id = auth_cookies.get('client_id') or None
        
        if access_token and client_id:
            self._session._set_auth_headers(access_token=access_token, client_id=client_id)
            return self._session
        else:
            self._session._set_auth_headers()
            return None
