# pylint: disable=R,C
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Author  : Nasir Khan (r0ot h3x49)
Github  : https://github.com/r0oth3x49
License : MIT


Copyright (c) 2018-2025 Nasir Khan (r0ot h3x49)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH 
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
from udemy.compat import conn_error, LOGIN_URL, cloudscraper
from udemy.logger import logger
from udemy.session import Session
from udemy.utils import (
    search_regex,
    hidden_inputs,
    to_configs,
    load_configs,
    extract_cookie_string,
)


class UdemyAuth(object):
    def __init__(self, username="", password="", cache_session=False):
        self.username = username
        self.password = password
        self._cache = cache_session
        self._session = Session()
        self._cloudsc = cloudscraper.create_scraper()

    def _form_hidden_input(self, form_id):
        try:
            resp = self._cloudsc.get(LOGIN_URL)  # pylint: disable=W
            resp.raise_for_status()
            webpage = resp.text
        except conn_error as error:
            raise error
        else:
            login_form = hidden_inputs(
                search_regex(
                    r'(?is)<form[^>]+?id=(["\'])%s\1[^>]*>(?P<form>.+?)</form>'
                    % form_id,
                    webpage,
                    "%s form" % form_id,
                    group="form",
                )
            )
            login_form.update({"email": self.username, "password": self.password})
            return login_form

    def is_session_exists(self):
        is_exists = False
        conf = load_configs()
        if conf:
            cookies = conf.get("cookies")
            if cookies:
                cookies = extract_cookie_string(cookies)
                access_token = cookies.get("access_token")
                client_id = cookies.get("client_id")
                self._session._set_auth_headers(  # pylint: disable=W
                    access_token=access_token, client_id=client_id
                )
                self._session._session.cookies.update(  # pylint: disable=W
                    {"access_token": access_token}
                )
                try:
                    url = "https://www.udemy.com/api-2.0/courses/"
                    resp = self._session._get(url)  # pylint: disable=W
                    resp.raise_for_status()
                    is_exists = True
                except Exception as error:  # pylint: disable=W
                    logger.error(
                        msg=f"Udemy Says: {error} session cookie seems to be expired..."
                    )
                    is_exists = False
        return is_exists, conf

    def authenticate(self, access_token="", client_id=""):
        if not access_token and not client_id:
            data = self._form_hidden_input(form_id="login-form")
            self._cloudsc.headers.update({"Referer": LOGIN_URL})
            auth_response = self._cloudsc.post(  # pylint: disable=W
                LOGIN_URL, data=data, allow_redirects=False
            )  # pylint: disable=W
            auth_cookies = auth_response.cookies

            access_token = auth_cookies.get("access_token", "")
            client_id = auth_cookies.get("client_id", "")

        if access_token:
            # dump cookies to configs
            if self._cache:
                _ = to_configs(
                    username=self.username,
                    password=self.password,
                    cookies=f"access_token={access_token}",
                )
            self._session._set_auth_headers(  # pylint: disable=W
                access_token=access_token, client_id=client_id
            )
            self._session._session.cookies.update(  # pylint: disable=W
                {"access_token": access_token}
            )
            return self._session, access_token
        else:
            self._session._set_auth_headers()  # pylint: disable=W
            return None, None
