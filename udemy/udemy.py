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

from udemy.internal import InternUdemyCourse as Udemy
from udemy.internal import InternUdemyCourses as UdemyCourses


def course(
    url,
    username="",
    password="",
    cookies="",
    basic=True,
    skip_hls_stream=False,
    cache_session=False,
    callback=None,
):
    """Returns udemy course instance.

    @params:
        url      : Udemy course url required : type (string).
        username : Udemy email account required : type (string).
        password : Udemy account password required : type (string)
        cookies  : Udemy account logged in browser cookies optional : type (string)
    """
    return Udemy(
        url,
        username,
        password,
        cookies,
        basic,
        skip_hls_stream,
        cache_session,
        callback,
    )


def fetch_enrolled_courses(username="", password="", cookies="", basic=True):
    """Returns udemy course instance.

    @params:
        url      : Udemy course url required : type (string).
        username : Udemy email account required : type (string).
        password : Udemy account password required : type (string)
        cookies  : Udemy account logged in browser cookies optional : type (string)
    """
    return UdemyCourses(username, password, cookies, basic)
