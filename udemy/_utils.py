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

from ._compat import (
                        os,
                        re,
                        sys,
                        json,
                        NO_DEFAULT,
                        compat_HTMLParser,
                        )

def cache_credentials(username, password, quality="", output=""):
    fname = "configuration"
    fmode = "w"
    creds = {
                "username"          : username,
                "password"          : password,
                "quality"           : quality,
                "output"            : output
            }
    fout = open(fname, fmode)
    json.dump(creds, fout, indent=4)
    fout.close()
    return "cached"

def use_cached_credentials():
    fname = "configuration"
    try:
        fout = open(fname)
    except IOError as e:
        creds = ''
        return creds
    except Exception as e:
        creds = ''
        return creds
    else:
        creds = json.load(fout)
        fout.close()
        return creds


# Thanks to a great open source utility youtube-dl ..
class HTMLAttributeParser(compat_HTMLParser):
    """Trivial HTML parser to gather the attributes for a single element"""
    def __init__(self):
        self.attrs = {}
        compat_HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)

def unescapeHTML(s):
    clean   = compat_HTMLParser()
    data    = clean.unescape(s)
    return data

def extract_attributes(html_element):
    """Given a string for an HTML element such as
    <el
         a="foo" B="bar" c="&98;az" d=boz
         empty= noval entity="&amp;"
         sq='"' dq="'"
    >
    Decode and return a dictionary of attributes.
    {
        'a': 'foo', 'b': 'bar', c: 'baz', d: 'boz',
        'empty': '', 'noval': None, 'entity': '&',
        'sq': '"', 'dq': '\''
    }.
    NB HTMLParser is stricter in Python 2.6 & 3.2 than in later versions,
    but the cases in the unit test will work for all of 2.6, 2.7, 3.2-3.5.
    """
    parser = HTMLAttributeParser()
    try:
        parser.feed(html_element)
        parser.close()
    except compat_HTMLParseError:
        pass
    return parser.attrs

def hidden_inputs(html):
    html = re.sub(r'<!--(?:(?!<!--).)*-->', '', html)
    hidden_inputs = {}
    for input in re.findall(r'(?i)(<input[^>]+>)', html):
        attrs = extract_attributes(input)
        if not input:
            continue
        if attrs.get('type') not in ('hidden', 'submit'):
            continue
        name = attrs.get('name') or attrs.get('id')
        value = attrs.get('value')
        if name and value is not None:
            hidden_inputs[name] = value
    return hidden_inputs

def search_regex(pattern, string, name, default=NO_DEFAULT, fatal=True, flags=0, group=None):
    """
    Perform a regex search on the given string, using a single or a list of
    patterns returning the first matching group.
    In case of failure return a default value or raise a WARNING or a
    RegexNotFoundError, depending on fatal, specifying the field name.
    """
    if isinstance(pattern, str):
        mobj = re.search(pattern, string, flags)
    else:
        for p in pattern:
            mobj = re.search(p, string, flags)
            if mobj:
                break

    _name = name

    if mobj:
        if group is None:
            # return the first matching group
            return next(g for g in mobj.groups() if g is not None)
        else:
            return mobj.group(group)
    elif default is not NO_DEFAULT:
        return default
    elif fatal:
        print('[-] Unable to extract %s' % _name)
        exit(0)
    else:
        print('[-] unable to extract %s' % _name)
        exit(0)

def parse_json(json_string, video_id, transform_source=None, fatal=True):
    if transform_source:
        json_string = transform_source(json_string)
    try:
        return json.loads(json_string)
    except ValueError as ve:
        errmsg = '[-] %s: Failed to parse JSON ' % video_id
        if fatal:
            print(errmsg, ve)
        else:
            print(errmsg + str(ve))

def js_to_json(code):
    COMMENT_RE = r'/\*(?:(?!\*/).)*?\*/|//[^\n]*'
    SKIP_RE = r'\s*(?:{comment})?\s*'.format(comment=COMMENT_RE)
    INTEGER_TABLE = (
        (r'(?s)^(0[xX][0-9a-fA-F]+){skip}:?$'.format(skip=SKIP_RE), 16),
        (r'(?s)^(0+[0-7]+){skip}:?$'.format(skip=SKIP_RE), 8),
    )

    def fix_kv(m):
        v = m.group(0)
        if v in ('true', 'false', 'null'):
            return v
        elif v.startswith('/*') or v.startswith('//') or v == ',':
            return ""

        if v[0] in ("'", '"'):
            v = re.sub(r'(?s)\\.|"', lambda m: {
                '"': '\\"',
                "\\'": "'",
                '\\\n': '',
                '\\x': '\\u00',
            }.get(m.group(0), m.group(0)), v[1:-1])

        for regex, base in INTEGER_TABLE:
            im = re.match(regex, v)
            if im:
                i = int(im.group(1), base)
                return '"%d":' % i if v.endswith(':') else '%d' % i

        return '"%s"' % v

    return re.sub(r'''(?sx)
        "(?:[^"\\]*(?:\\\\|\\['"nurtbfx/\n]))*[^"\\]*"|
        '(?:[^'\\]*(?:\\\\|\\['"nurtbfx/\n]))*[^'\\]*'|
        {comment}|,(?={skip}[\]}}])|
        [a-zA-Z_][.a-zA-Z_0-9]*|
        \b(?:0[xX][0-9a-fA-F]+|0+[0-7]+)(?:{skip}:)?|
        [0-9]+(?={skip}:)
        '''.format(comment=COMMENT_RE, skip=SKIP_RE), fix_kv, code)
