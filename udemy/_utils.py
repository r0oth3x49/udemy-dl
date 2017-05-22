#!/usr/bin/python


from . import __author__
from . import __version__
from ._compat import (
                        re,
                        json,
                        NO_DEFAULT,
                        compat_HTMLParser,
                        )


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
