#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=R,C,E,W

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

from udemy.compat import (
    re,
    os,
    sys,
    json,
    NO_DEFAULT,
    compat_HTMLParser,
)
from udemy.logger import logger


def extract_cookie_string(raw_cookies):
    cookies = {}
    try:
        access_token = re.search(
            r"(?i)(?:access_token=(?P<access_token>\w+))", raw_cookies
        )
    except Exception as error:
        logger.error(
            msg=f"Cookies error, {error}, unable to extract access_token from cookies."
        )
        sys.exit(0)
    if not access_token:
        logger.error(msg="Unable to find access_token, proper cookies required")
        logger.info(
            msg="follow: https://github.com/r0oth3x49/udemy-dl#how-to-login-with-cookie",
            new_line=True,
        )
        sys.stdout.flush()
        sys.exit(0)
    access_token = access_token.group("access_token")
    cookies.update({"access_token": access_token})
    return cookies


def extract_url_or_courses(url_or_filepath):
    courses = []
    if os.path.isfile(url_or_filepath):
        courses = [i.strip() for i in open(url_or_filepath)]
    if not os.path.isfile(url_or_filepath):
        courses = [url_or_filepath]
    return courses


def to_human_readable(content_length):
    hr = ""
    if content_length <= 1048576.00:
        size = round(float(content_length) / 1024.00, 2)
        sz = format(size if size < 1024.00 else size / 1024.00, ".2f",)
        in_MB = "KB" if size < 1024.00 else "MB"
    else:
        size = round(float(content_length) / 1048576, 2)
        sz = format(size if size < 1024.00 else size / 1024.00, ".2f",)
        in_MB = "MB " if size < 1024.00 else "GB "
    hr = f"{sz}{in_MB}"
    return hr


def to_filepath(base, name):
    base = re.sub(r'"', "", base.strip())
    filepath = os.path.join(base, name)
    try:
        os.makedirs(filepath)
    except:
        pass
    return filepath


def prepare_html(title, html):
    data = """
                <html>
                <head>
                <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
                <title>%s</title>
                </head>
                <body>
                <div class="container">
                <div class="row">
                <div class="col-md-10 col-md-offset-1">
                    <p class="lead">%s</p>
                </div>
                </div>
                </div>
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
                </body>
                </html>
                """ % (
        title,
        html,
    )
    return data.encode("utf-8")


def to_file(filename, fmode, content, encoding="utf-8", errors="ignore"):
    retVal = {}

    try:
        with open(filename, fmode, encoding=encoding, errors=errors) as fd:
            fd.write(content)
        retVal = {"status": "True", "msg": "download"}
    except (OSError, Exception, UnicodeDecodeError) as e:
        retVal = {"status": "False", "msg": "{}".format(e)}

    return retVal


def to_configs(
    username="", password="", cookies="", quality="", output="", language=""
):
    configs = load_configs()
    fname = ".udemy-dl.conf"
    fmode = "w"
    if configs:
        cfu = configs.get("username")
        cfp = configs.get("password")
        cfc = configs.get("cookies")
        cfq = configs.get("quality")
        cfl = configs.get("language")
        cfo = configs.get("output")
        if cfo:
            cfo = re.sub(r'"', "", cfo.strip())
        if username and cfu != username:
            configs.update({"username": username})
        if password and cfp != password:
            configs.update({"password": password})
        if cookies and cfc != cookies:
            configs.update({"cookies": cookies})
        if quality and cfq != quality:
            configs.update({"quality": quality})
        if language and cfl != language:
            configs.update({"language": language})
        if output and cfo != output:
            output = re.sub(r'"', "", output.strip())
            configs.update({"output": output})
        with open(fname, fmode) as fd:
            json.dump(configs, fd, indent=4)
    if not configs:
        if output:
            output = re.sub(r'"', "", output.strip())
        creds = {
            "username": username,
            "password": password,
            "quality": quality,
            "output": output,
            "language": language,
            "cookies": cookies,
        }
        with open(fname, fmode) as fd:
            json.dump(creds, fd, indent=4)
    return "cached"


def load_configs():
    fname = ".udemy-dl.conf"
    configs = {}
    if os.path.isfile(fname):
        with open(fname) as fd:
            configs = json.load(fd)
    return configs


# Thanks to a great open source utility youtube-dl ..
class HTMLAttributeParser(compat_HTMLParser):  # pylint: disable=W
    """Trivial HTML parser to gather the attributes for a single element"""

    def __init__(self):
        self.attrs = {}
        compat_HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)


def unescapeHTML(s):
    clean = compat_HTMLParser()
    if hasattr(clean, "unescape"):
        data = clean.unescape(s)
    if not hasattr(clean, "unescape"):
        # Python 3.9.0 HTML_Parser unescape attribute deprecated
        # https://github.com/pypa/setuptools/pull/1788/files
        import html
        data = html.unescape(s)
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
    except Exception:  # pylint: disable=W
        pass
    return parser.attrs


def hidden_inputs(html):
    html = re.sub(r"<!--(?:(?!<!--).)*-->", "", html)
    hidden_inputs = {}  # pylint: disable=W
    for entry in re.findall(r"(?i)(<input[^>]+>)", html):
        attrs = extract_attributes(entry)
        if not entry:
            continue
        if attrs.get("type") not in ("hidden", "submit"):
            continue
        name = attrs.get("name") or attrs.get("id")
        value = attrs.get("value")
        if name and value is not None:
            hidden_inputs[name] = value
    return hidden_inputs


def search_regex(
    pattern, string, name, default=NO_DEFAULT, fatal=True, flags=0, group=None
):
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
        print("[-] Unable to extract %s" % _name)
        exit(0)
    else:
        print("[-] unable to extract %s" % _name)
        exit(0)


def parse_json(json_string, video_id, transform_source=None, fatal=True):
    if transform_source:
        json_string = transform_source(json_string)
    try:
        return json.loads(json_string)
    except ValueError as ve:
        errmsg = "[-] %s: Failed to parse JSON " % video_id
        if fatal:
            print(errmsg, ve)
        else:
            print(errmsg + str(ve))


def js_to_json(code):
    COMMENT_RE = r"/\*(?:(?!\*/).)*?\*/|//[^\n]*"
    SKIP_RE = r"\s*(?:{comment})?\s*".format(comment=COMMENT_RE)
    INTEGER_TABLE = (
        (r"(?s)^(0[xX][0-9a-fA-F]+){skip}:?$".format(skip=SKIP_RE), 16),
        (r"(?s)^(0+[0-7]+){skip}:?$".format(skip=SKIP_RE), 8),
    )

    def fix_kv(m):
        v = m.group(0)
        if v in ("true", "false", "null"):
            return v
        elif v.startswith("/*") or v.startswith("//") or v == ",":
            return ""

        if v[0] in ("'", '"'):
            v = re.sub(
                r'(?s)\\.|"',
                lambda m: {'"': '\\"', "\\'": "'", "\\\n": "", "\\x": "\\u00",}.get(
                    m.group(0), m.group(0)
                ),
                v[1:-1],
            )

        for regex, base in INTEGER_TABLE:
            im = re.match(regex, v)
            if im:
                i = int(im.group(1), base)
                return '"%d":' % i if v.endswith(":") else "%d" % i

        return '"%s"' % v

    return re.sub(
        r"""(?sx)
        "(?:[^"\\]*(?:\\\\|\\['"nurtbfx/\n]))*[^"\\]*"|
        '(?:[^'\\]*(?:\\\\|\\['"nurtbfx/\n]))*[^'\\]*'|
        {comment}|,(?={skip}[\]}}])|
        [a-zA-Z_][.a-zA-Z_0-9]*|
        \b(?:0[xX][0-9a-fA-F]+|0+[0-7]+)(?:{skip}:)?|
        [0-9]+(?={skip}:)
        """.format(
            comment=COMMENT_RE, skip=SKIP_RE
        ),
        fix_kv,
        code,
    )
