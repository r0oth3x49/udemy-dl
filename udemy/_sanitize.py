#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from ._compat import (
                        re, 
                        os
                    )


def sanitize_title(title):
    _locale = {
    # Turkish Characters to English
        # Capital chars
                '194'  : 'A',
                '199'  : 'C',
                '286'  : 'G',
                '304'  : 'I',
                '206'  : 'I',
                '214'  : 'O',
                '350'  : 'S',
                '219'  : 'U',
        # Small chars
                '226'  : 'a',
                '231'  : 'c',
                '287'  : 'g',
                '305'  : 'i',
                '238'  : 'i',
                '246'  : 'o',
                '351'  : 's',
                '251'  : 'u',
    # Spanish Characters to English
        # Small chars
                '191'  : '',
                '225'  : 'a',
                '233'  : 'e',
                '237'  : 'i',
                '243'  : 'o',
                '250'  : 'u',
                '252'  : 'u',
                '168u' : 'u',
                '241'  : 'n',
        # Capital chars
                '193'  : 'A',
                '201'  : 'E',
                '205'  : 'I',
                '211'  : 'O',
                '218'  : 'U',
                '220'  : 'U',
                '168U' : 'U',
                '209'  : 'N',
    }
    _temp   = ''.join([str(ord(i)) if ord(i) > 128 else i for i in title])
    for _ascii,_char in _locale.items():
        if _ascii in _temp:
            _temp = _temp.replace(_ascii, _char)

    ok = re.compile(r'[^/]')
    if os.name == "nt":
        ok = re.compile(r'[^\\/:.*?"<>|,]')

    _title      = ''.join(x if ok.match(x) else "_" for x in _temp)

    return _title
