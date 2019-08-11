#!/usr/bin/python

'''

Author  : Nasir Khan (r0ot h3x49)
Github  : https://github.com/r0oth3x49
License : MIT


Copyright (c) 2018 Nasir Khan (r0ot h3x49)
Copyright (c) 2019 Kais Ben Salah

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH 
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from os import system

from ._compat import (
                re,
                os,
                sys,
                time,
                pyver,
                codecs,
                compat_urlerr,
                compat_opener,
                compat_request,
                compat_urlopen,
                compat_httperr,
                HEADERS
    )

early_py_version = sys.version_info[:2] < (2, 7)

class Downloader(object):

    def __init__(self):
        self._filename = None
        self._url = None

    @property
    def url(self):
        return self._url

    @property
    def filename(self):
        if not self._filename:
            self._filename = self._generate_filename()
        return self._filename

    @property
    def unsafe_filename(self):
        if not self._filename:
            self._filename = self._generate_unsafe_filename()
        return self._filename

    def _generate_filename():
        pass

    def _generate_unsafe_filename():
        pass

    def _call_wget(self, src, dst):
        src = '"%s"' % src
        dst = "'%s'" % dst
        cmd = 'wget -c -O %s %s' % (dst, src)
        system(cmd)

    def download(self, filepath="", unsafe=False, quiet=False, callback=lambda *x: None):
        savedir = filename = ""

        if filepath and os.path.isdir(filepath):
            savedir, filename = filepath, self.filename if not unsafe else self.unsafe_filename

        elif filepath:
            savedir, filename = os.path.split(filepath)

        else:
            filename = self.filename if not unsafe else self.unsafe_filename

        filepath = os.path.join(savedir, filename)

        self._call_wget(self.url, filepath)

        return {"status" : "True", "msg" : "download"}

class UdemyCourse(object):

    def __init__(self, url, username='', password='', cookies='', basic=True, callback=None):

        self._url = url
        self._username = username
        self._password = password
        self._cookies = cookies 
        self._callback = callback or (lambda x: None)
        self._have_basic = False

        self._id = None
        self._title = None
        self._chapters_count = None
        self._total_lectures = None

        self._chapters = []

        if basic:
            self._fetch_course()

    def _fetch_course(self):
        raise NotImplementedError

    @property
    def id(self):
        if not self._id:
            self._fetch_course()
        return self._id

    @property
    def title(self):
        if not self._title:
            self._fetch_course()
        return self._title

    @property
    def chapters(self):
        if not self._chapters_count:
            self._fetch_course()
        return self._chapters_count

    @property
    def lectures(self):
        if not self._total_lectures:
            self._fetch_course()
        return self._total_lectures

    def get_chapters(self):
        if not self._chapters:
            self._fetch_course()
        return self._chapters

class UdemyChapters(object):

    def __init__(self):

        self._chapter_id = None
        self._chapter_index = None
        self._chapter_title = None
        self._unsafe_title = None
        self._lectures_count = None

        self._lectures = []

    def __repr__(self):
        chapter = "{title}".format(title=self.title)
        return chapter

    @property
    def id(self):
        return self._chapter_id

    @property
    def index(self):
        return self._chapter_index

    @property
    def title(self):
        return self._chapter_title

    @property
    def unsafe_title(self):
        return self._unsafe_title
    
    @property
    def lectures(self):
        return self._lectures_count

    def get_lectures(self):
        return self._lectures

class UdemyLectures(object):

    def __init__(self):

        self._best = None
        self._duration = None
        self._extension = None
        self._lecture_id = None
        self._lecture_title  =   None
        self._unsafe_title = None
        self._lecture_index = None
        self._sources_count = None
        self._assets_count = None
        self._subtitles_count = None
        self._html_content = None

        self._assets = []
        self._streams = []
        self._subtitles = []

    def __repr__(self):
        lecture = "{title}".format(title=self.title)
        return lecture
    
    @property
    def id(self):
        return self._lecture_id

    @property
    def index(self):
        return self._lecture_index

    @property
    def title(self):
        return self._lecture_title

    @property
    def unsafe_title(self):
        return self._unsafe_title

    @property
    def html(self):
        return self._html_content
    
    @property
    def duration(self):
        return self._duration

    @property
    def extension(self):
        return self._extension

    @property
    def assets(self):
        if not self._assets:
            self._process_assets()
        return self._assets

    @property
    def streams(self):
        if not self._streams:
            self._process_streams()
        return self._streams

    @property
    def subtitles(self):
        if not self._subtitles:
            self._process_subtitles()
        return self._subtitles

    def _getbest(self):
        streams = self.streams
        if not streams:
            return None
        def _sortkey(x, keyres=0, keyftype=0):
            keyres = int(x.resolution.split('x')[0])
            keyftype = x.extension
            st = (keyftype, keyres)
            return st
        
        self._best = max(streams, key=_sortkey)
        return self._best

    def getbest(self):
        return self._getbest()

    def dump(self, filepath, unsafe=False):
        retVal = {}
        data = '''
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
                ''' % (self.title, self.html)
        html = data.encode('utf-8').strip()
        if not unsafe:
            filename = "%s\\%s" % (filepath, self.title) if os.name == 'nt' else "%s/%s" % (filepath, self.title)
            filename += ".html"
        if unsafe:
            filename = u"%s\\%s" % (filepath, self.unsafe_title) if os.name == 'nt' else u"%s/%s" % (filepath, self.unsafe_title)
            filename += ".html"

        if os.path.isfile(filename):
            retVal = {"status" : "True", "msg" : "already downloaded"}
            return retVal
        
        try:
            f = codecs.open(filename, 'wb', errors='ignore')
            f.write(html)
        except (OSError, Exception, UnicodeDecodeError) as e:
            retVal = {'status' : 'False', 'msg' : '{}'.format(e)}
        else:
            retVal = {'status' : 'True', 'msg' : 'download'}
            f.close()

        return retVal

class UdemyLectureStream(Downloader):

    def __init__(self, parent):

        Downloader.__init__(self)

        self._mediatype = None
        self._quality = None
        self._resolution = None
        self._dimention = None
        self._extension = None

        self._parent = parent
        self._fsize = None
        self._active = False

    def __repr__(self):
        out = "%s:%s@%s" % (self.mediatype, self.extension, self.quality)
        return out

    def _generate_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.title)
        filename += "." + self.extension
        return filename

    def _generate_unsafe_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.unsafe_title)
        filename += "." + self.extension
        return filename

    @property
    def resolution(self):
        return self._resolution

    @property
    def quality(self):
        return self._quality

    @property
    def id(self):
        return self._parent.id

    @property
    def dimention(self):
        return self._dimention

    @property
    def extension(self):
        return self._extension

    @property
    def title(self):
        return self._parent.title

    @property
    def unsafe_title(self):
        return self._parent.unsafe_title

    @property
    def mediatype(self):
        return self._mediatype

    def get_filesize(self):
        if not self._fsize:
            try:
                cl = 'content-length'
                opener = compat_opener()
                opener.addheaders = [('User-Agent', HEADERS.get('User-Agent'))]
                self._fsize = int(opener.open(self.url).headers[cl])
            except (compat_urlerr, compat_httperr):
                self._fsize = 0
        return self._fsize

class UdemyLectureAssets(Downloader):

    def __init__(self, parent):

        self._extension = None
        self._mediatype = None

        self._parent = parent
        self._fsize = None
        self._active = False

    def __repr__(self):
        out = "%s:%s@%s" % (self.mediatype, self.extension, self.extension)
        return out

    def _generate_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.title)
        filename += ".{}".format(self.extension)
        return filename

    def _generate_unsafe_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.unsafe_title)
        filename += ".{}".format(self.extension)
        return filename

    def _write_external_links(self, filepath, unsafe=False):
        retVal = {}
        filename = filepath

        try:
            filename += '.txt' if not unsafe else u'.txt'
            f = codecs.open(filename, 'a', encoding='utf-8', errors='ignore')
            data = '{}\n'.format(self.url) if not unsafe else u'{}\n'.format(self.url)
            f.write(data)
        except (OSError, Exception, UnicodeDecodeError) as e:
            retVal = {'status' : 'False', 'msg' : '{}'.format(e)}
        else:
            retVal = {'status' : 'True', 'msg' : 'download'}
            f.close()

        return retVal

    @property
    def id(self):
        return self._parent.id

    @property
    def extension(self):
        return self._extension

    @property
    def title(self):
        return self._parent.title

    @property
    def unsafe_title(self):
        return self._parent.unsafe_title

    @property
    def mediatype(self):
        return self._mediatype

    def get_filesize(self):
        if not self._fsize:
            try:
                cl = 'content-length'
                opener = compat_opener()
                opener.addheaders = [('User-Agent', HEADERS.get('User-Agent'))]
                self._fsize = int(opener.open(self.url).headers[cl])
            except (compat_urlerr, compat_httperr):
                self._fsize = 0
        return self._fsize

class UdemyLectureSubtitles(Downloader):

    def __init__(self, parent):

        self._mediatype = None
        self._extension = None
        self._language = None
        self._url = None

        self._parent = parent
        self._filename = None
        self._fsize = None
        self._active = False

    def __repr__(self):
        out = "%s:%s@%s" % (self.mediatype, self.language, self.extension)
        return out

    def _generate_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.title)
        filename += "-{}.{}".format(self.language, self.extension)
        return filename

    def _generate_unsafe_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.unsafe_title)
        filename += "-{}.{}".format(self.language, self.extension)
        return filename

    @property
    def id(self):
        return self._parent.id
    
    @property
    def url(self):
        return self._url

    @property
    def extension(self):
        return self._extension

    @property
    def language(self):
        return self._language

    @property
    def title(self):
        return self._parent.title

    @property
    def unsafe_title(self):
        return self._parent.unsafe_title

    @property
    def filename(self):
        if not self._filename:
            self._filename = self._generate_filename()
        return self._filename

    @property
    def unsafe_filename(self):
        if not self._filename:
            self._filename = self._generate_unsafe_filename()
        return self._filename

    @property
    def mediatype(self):
        return self._mediatype

    def get_filesize(self):
        if not self._fsize:
            try:
                cl = 'content-length'
                opener = compat_opener()
                opener.addheaders = [('User-Agent', HEADERS.get('User-Agent'))]
                self._fsize = int(opener.open(self.url).headers[cl])
            except (compat_urlerr, compat_httperr):
                self._fsize = 0
        return self._fsize
