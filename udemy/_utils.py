#!/usr/bin/python


from . import __author__
from . import __version__
from ._compat import (
                        re,
                        json,
                        NO_DEFAULT,
                        compat_HTMLParser,
                        )


def cache_credentials(username, password):
    fname = "credentials"
    fmode = "w"
    creds = {
                "username" : username,
                "password" : password
            }
    fout = open(fname, fmode)
    json.dump(creds, fout)
    fout.close()
    return "cached"


def use_cached_credentials():
    fname = "credentials"
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
        

def unescapeHTML(s):
    clean   = compat_HTMLParser()
    data    = clean.unescape(s)
    return data

def _search_regex(pattern, string, name, default=NO_DEFAULT, fatal=True, flags=0, group=None):
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
    else:
        print('[-] unable to extract %s' % _name)
        return None

def _parse_json(json_string, video_id, transform_source=None, fatal=True):
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

def _search_simple_regex(regex, webpage):
    _extract = re.search(regex, webpage)
    return _extract

# thanks to youtube-dl
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
