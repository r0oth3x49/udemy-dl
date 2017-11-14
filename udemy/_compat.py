#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from . import __author__
from . import __version__
if sys.version_info[:2] >= (3, 0):
    import re
    import ssl
    import json
    import requests
    import urllib.request as compat_urllib

    from ast                    import literal_eval     as compat_ConvertToDict
    from requests               import get              as compat_get
    from urllib.error           import HTTPError        as compat_httperr
    from urllib.error           import URLError         as compat_urlerr
    from urllib.parse           import urlparse         as compat_urlparse
    from urllib.request         import Request          as compat_request
    from urllib.request         import urlopen          as compat_urlopen
    from urllib.request         import build_opener     as compat_opener
    from html.parser            import HTMLParser       as compat_HTMLParser
    from requests.exceptions    import ConnectionError  as conn_error

    compat_str, pyver = str, 3
    ssl._create_default_https_context = ssl._create_unverified_context
    
else:
    import re
    import json
    import requests
    import urllib2 as compat_urllib

    from ast                 import literal_eval    as compat_ConvertToDict
    from requests            import get             as compat_get
    from urllib2             import Request         as compat_request
    from urllib2             import urlopen         as compat_urlopen
    from urllib2             import URLError        as compat_urlerr
    from urllib2             import HTTPError       as compat_httperr
    from urllib2             import build_opener    as compat_opener
    from urlparse            import urlparse        as compat_urlparse
    from HTMLParser          import HTMLParser      as compat_HTMLParser
    from requests.exceptions import ConnectionError as conn_error

    compat_str, pyver = unicode, 2

NO_DEFAULT          = object()
login_url           = 'https://www.udemy.com/join/login-popup/?displayType=ajax&display_type=popup&showSkipButton=1&returnUrlAfterLogin=https%3A%2F%2Fwww.udemy.com%2F&next=https%3A%2F%2Fwww.udemy.com%2F&locale=en_US'
login_popup         = 'https://www.udemy.com/join/login-popup'
logout              = 'http://www.udemy.com/user/logout'
course_list         = 'https://www.udemy.com/api-2.0/courses/?page_size=10000'
course_url          = 'https://www.udemy.com/api-2.0/courses/{course_id}/cached-subscriber-curriculum-items?fields[asset]=results,external_url,download_urls,slide_urls,filename,asset_type&fields[chapter]=object_index,title,sort_order&fields[lecture]=id,title,object_index,asset,supplementary_assets,view_html,sort_order&page_size=100000'
get_url             = 'https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/lectures/{lecture_id}?fields[lecture]=view_html,asset'
attached_file_url   = 'https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/lectures/{lecture_id}/supplementary-assets/{asset_id}?fields[asset]=download_urls'
num_lectures        = 'https://www.udemy.com/api-2.0/courses/{course_id}?fields[course]=num_lectures'
user_agent          = "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/47.0 (Chrome)"
std_headers         =   {
                        'User-Agent'        : 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/47.0 (Chrome)',
                        'X-Requested-With'  : 'XMLHttpRequest',
                        'Host'              : 'www.udemy.com',
                        'Referer'           : 'https://www.udemy.com/join/login-popup'
                        }

__ALL__ =[
            "course_list"
            "conn_error",
            "attached_file_url"
            "compat_ConvertToDict",
            "compat_request",
            "num_lectures",
            "compat_get",
            "requests",
            "logout",
            "json",
            "re",
            "compat_str",
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
            "NO_DEFAULT",
    ]
