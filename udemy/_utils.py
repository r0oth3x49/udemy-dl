#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import __author__
from . import __version__
from ._compat import (
                        os,
                        re,
                        sys,
                        json,
                        NO_DEFAULT,
                        compat_HTMLParser,
                        )


def cache_credentials(username, password, resolution="", output=""):
    fname = "configuration"
    fmode = "w"
    creds = {
                "username"          : username,
                "password"          : password,
                "resolution"        : resolution,
                "output"            : output
            }
    fout = open(fname, fmode)
    json.dump(creds, fout)
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

class HTMLAttributeParser(compat_HTMLParser):
    """Trivial HTML parser to gather the attributes for a single element"""
    def __init__(self):
        self.attrs = {}
        compat_HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)

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

def _hidden_inputs(html):
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

class WEBVTT2SRT:
    def _fix_subtitles(self, content):
        _container = ''
        for line in content[2:]:
            if sys.version_info[:2] >= (3, 0):
                _container += line.decode('utf-8', 'ignore')
            else:
                _container += line
        caption = re.sub(r"(\d{2}:\d{2}:\d{2})(\.)(\d{3})", r'\1,\3', _container)
        return caption

    def _generate_timecode(self, timecode):
        _timecode   =   ""
        if isinstance(timecode, list):
            if len(timecode) < 3:
                hh, mm, ss, tt = '00', timecode[0], timecode[1].split('.')[0], timecode[1].split('.')[-1]
                _timecode     = '{}:{}:{},{}'.format(hh, mm, ss, tt)
            if len(timecode) == 3:
                hh, mm, ss, tt = timecode[0], timecode[1], timecode[2].split('.')[0], timecode[2].split('.')[-1]
                _timecode     = '{}:{}:{},{}'.format(hh, mm, ss, tt)
        return _timecode

    def convert(self, filename=None):
        _flag = {}
        if filename:

            _seqcounter     =   0
            _appeartime     =   None
            _disappertime   =   None
            _textcontainer  =   None


            _srtcontent     =   ""
            _srtfilename    =   filename.replace('.vtt', '.srt')

            # open and save file content into list for parsing ...
            try:
                f_in        =   open(filename, 'rb')
            except Exception as e:
                _flag = {'status' : 'False', 'msg' : 'failed to open file : file not found ..'}
            else:
                content     =   [line for line in (l.decode('utf-8', 'ignore').strip() for l in f_in) if line]
                f_in.close()
                if len(content) > 4:
                    if content[0] == 'WEBVTT' or content[0].endswith('WEBVTT') or 'WEBVTT' in content[0]:
                        if content[1] == '1':
                            f           = open(filename, 'rb')
                            content     = f.readlines()
                            f.close()
                            _srtcontent = self._fix_subtitles(content)
                        else:
                            for line in content[1:]:
                                if '-->' in line:
                                    _start, _end  = line.split(' --> ')
                                    _stcode       = _start.split(':')
                                    _etcode       = _end.split(':')
                                    _appeartime   = self._generate_timecode(_stcode)
                                    _disappertime = self._generate_timecode(_etcode)
                                else:
                                    _seqcounter     +=  1
                                    line             = ''.join([text if ord(text) < 128 else '' for text in line])
                                    _textcontainer   = '{}'.format(line)
                                    if _textcontainer:
                                        _srtcontent += '{}\r\n{} --> {}\r\n{}\r\n\r\n'.format(_seqcounter, _appeartime, _disappertime, _textcontainer)

                        if _srtcontent:
                            with open(_srtfilename, 'w') as sub:
                                sub.write('{}'.format(_srtcontent))
                            sub.close()
                            try:
                                os.unlink(filename)
                            except Exception as e:
                                pass
                            _flag = {'status' : 'True', 'msg' : 'successfully generated subtitle in srt ...'}
                else:
                    _flag = {'status' : 'False', 'msg' : 'subtitle file seems to be empty skipping conversion from WEBVTT to SRT ..'}
        return _flag