#!/usr/bin/python



from ._compat import (
                        compat_HTMLParser,
                        re,
                        compat_ConvertToDict,
                        )

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
    parser.feed(html_element)
    parser.close()
    return parser.attrs

def extract_videojs_data(html_element):
    parser          = compat_HTMLParser()
    data            = html_element.strip().split('videojs-setup-data="')[1].split('"')[0]
    html_escape     = parser.unescape(data)
    clean           = re.findall(r'(.ources":.*\}])', html_escape if not "\n" in html_escape else html_escape.replace("\n", ''), re.M|re.I)[0] if not None else "None"#re.findall(r'"sources":(.*}])', html_escape, re.M|re.I)[0] if not None else "None"
    cleaned_data    = clean[10:-1]
    Val             = cleaned_data.split('],') if "]" in cleaned_data else cleaned_data
    retVal          = Val[0] if type(Val) is list else Val
    try:
        vid_dict    = compat_ConvertToDict(retVal)
    except Exception as e:
        pass
    else:
        if type(vid_dict) is dict:
            return vid_dict
        else:
            return vid_dict

def unescapeHTML(json_data):
    clean   = compat_HTMLParser()
    data    = clean.unescape(json_data)
    return data

def _search_regex(regex, webpage):
    _extract = re.search(regex, webpage)
    return _extract

def _convert_to_dict(data):
    _dict = compat_ConvertToDict(str(data[1:-1]))
    return _dict
    
