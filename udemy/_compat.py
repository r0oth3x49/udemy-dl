#!/usr/bin/env python
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

import re
import os
import sys
import time
import json
import codecs
import requests
if sys.version_info[:2] >= (3, 0):

    import ssl
    import urllib.request as compat_urllib

    from urllib.error import HTTPError as compat_httperr
    from urllib.error import URLError as compat_urlerr
    from urllib.parse import urlparse as compat_urlparse
    from urllib.request import Request as compat_request
    from urllib.request import urlopen as compat_urlopen
    from urllib.request import build_opener as compat_opener
    from html.parser import HTMLParser as compat_HTMLParser
    from http.cookies import SimpleCookie as ParseCookie
    from requests.exceptions import ConnectionError as conn_error

    encoding, pyver = str, 3
    ssl._create_default_https_context = ssl._create_unverified_context
    
else:
    
    import urllib2 as compat_urllib

    from urllib2 import Request as compat_request
    from urllib2 import urlopen as compat_urlopen
    from urllib2 import URLError as compat_urlerr
    from urllib2 import HTTPError as compat_httperr
    from urllib2 import build_opener as compat_opener
    from urlparse import urlparse as compat_urlparse
    from Cookie import SimpleCookie as ParseCookie
    from HTMLParser import HTMLParser as compat_HTMLParser
    from requests.exceptions import ConnectionError as conn_error

    encoding, pyver = unicode, 2


NO_DEFAULT = object()
LOGIN_URL = 'https://www.udemy.com/join/login-popup/?displayType=ajax&display_type=popup&showSkipButton=1&returnUrlAfterLogin=https'#'https://www.udemy.com/api-2.0/auth/udemy-auth/login/?fields[user]=access_token'
LOGOUT_URL = 'https://www.udemy.com/user/logout'

WISHLIST_URL = "https://{portal_name}.udemy.com/api-2.0/users/me/wishlisted-courses?fields[course]=id,url,published_title&ordering=-access_time&page=1&page_size=1000"
COLLECTION_URL = "https://{portal_name}.udemy.com/api-2.0/users/me/subscribed-courses-collections/?collection_has_courses=True&course_limit=20&fields[course]=last_accessed_time,published_title&fields[user_has_subscribed_courses_collection]=@all&page=1&page_size=1000"
MY_COURSES_URL = "https://{portal_name}.udemy.com/api-2.0/users/me/subscribed-courses?fields[course]=id,url,published_title&ordering=-last_accessed,-access_time&page=1&page_size=10000"
COURSE_SEARCH = "https://{portal_name}.udemy.com/api-2.0/users/me/subscribed-courses?fields[course]=id,url,published_title&page=1&page_size=1000&ordering=-last_accessed,-access_time&search={course_name}"
COURSE_URL = 'https://{portal_name}.udemy.com/api-2.0/courses/{course_id}/cached-subscriber-curriculum-items?fields[asset]=results,external_url,time_estimation,download_urls,slide_urls,filename,asset_type,captions,stream_urls,body&fields[chapter]=object_index,title,sort_order&fields[lecture]=id,title,object_index,asset,supplementary_assets,view_html&page_size=10000'
HEADERS = {
            'Origin': 'www.udemy.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
            'Referer': 'https://www.udemy.com/join/login-popup/',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
            }


__ALL__ = [
    're',
    'os',
    'sys',
    'time',
    'json',
    'pyver',
    'codecs',
    'encoding',
    'requests',
    'conn_error',
    'compat_urlerr',
    'compat_opener',
    'compat_urllib',
    'compat_urlopen',
    'compat_request',
    'compat_httperr',
    'compat_urlparse',
    'compat_HTMLParser',
    'ParseCookie',
    'HEADERS',
    'LOGIN_URL',
    'NO_DEFAULT',
    'COURSE_URL',
    'LOGOUT_URL',
    'WISHLIST_URL',
    'COLLECTION_URL',
    'MY_COURSES_URL',
    'COURSE_SEARCH'
    ]
