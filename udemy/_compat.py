#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

if sys.version_info[:2] >= (3, 0):
    import requests,re,json
    from requests import get as compat_get
    import urllib.request as compat_urllib
    from urllib.request import Request as compat_request
    from urllib.request import urlopen as compat_urlopen
    from urllib.error import HTTPError as compat_httperr
    from urllib.error import URLError as compat_urlerr
    from urllib.parse import urlparse as compat_urlparse
    from urllib.request import build_opener as compat_opener
    from html.parser import HTMLParser as compat_HTMLParser
    from ast import literal_eval as compat_ConvertToDict
    uni, pyver = str, 3
    
else:
    import requests,re,json
    from requests import get as compat_get
    import urllib2 as compat_urllib
    from urllib2 import Request as compat_request
    from urllib2 import urlopen as compat_urlopen
    from urllib2 import URLError as compat_urlerr
    from urllib2 import HTTPError as compat_httperr
    from urlparse import urlparse as compat_urlparse
    from urllib2 import build_opener as compat_opener
    from HTMLParser import HTMLParser as compat_HTMLParser
    from ast import literal_eval as compat_ConvertToDict
    uni, pyver = unicode, 2


login_url = 'https://www.udemy.com/join/login-popup/?displayType=ajax&display_type=popup&showSkipButton=1&returnUrlAfterLogin=https%3A%2F%2Fwww.udemy.com%2F&next=https%3A%2F%2Fwww.udemy.com%2F&locale=en_US'
login_popup = 'https://www.udemy.com/join/login-popup'
logout = 'http://www.udemy.com/user/logout'
course_url = 'https://www.udemy.com/api-2.0/courses/%s/cached-subscriber-curriculum-items?fields[asset]=results,asset_type&fields[chapter]=object_index,title,sort_order&fields[lecture]=id,title,object_index,asset,view_html,sort_order&page_size=100000'
get_url = 'https://www.udemy.com/api-2.0/users/me/subscribed-courses/%s/lectures/%s?fields[lecture]=view_html,asset'
num_lectures = 'https://www.udemy.com/api-2.0/courses/%s?fields[course]=num_lectures'
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/47.0 (Chrome)"
std_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/47.0 (Chrome)',
    'X-Requested-With': 'XMLHttpRequest',
    'Host': 'www.udemy.com',
    'Referer': 'https://www.udemy.com/join/login-popup'}

__ALL__ =[
    "compat_ConvertToDict",
    "compat_request",
    "num_lectures",
    "compat_get",
    "requests",
    "logout",
    "re",
    "login_popup",
    "compat_urllib",
    "compat_urlparse",
    "compat_urlerr",
    "compat_httperr",
    "login_url",
    "course_url",
    "get_url",
    "std_headers",
    "compat_urlopen",
    "compat_opener",
    "user_agent",
    "compat_HTMLParser",
    ]
