#!/usr/bin/python

"""

Author  : Nasir Khan (r0ot h3x49)
Github  : https://github.com/r0oth3x49
License : MIT


Copyright (c) 2020 Nasir Khan (r0ot h3x49)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH 
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
from ._compat import (
                re,
                os,
                sys,
                time,
                pyver,
                codecs,
                requests,
                conn_error,
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
        self._url = None
        self._filename = None
        self._mediatype = None
        self._extension = None
        self._sess = requests.session()

    @property
    def url(self):
        """abac"""
        return self._url

    @property
    def mediatype(self):
        return self._mediatype

    @property
    def extension(self):
        return self._extension

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

    def _write_external_links(self, filepath, unsafe=False):
        retVal = {}
        savedirs, name = os.path.split(filepath)
        filename = 'external-assets-links.txt' if not unsafe else u'external-assets-links.txt'
        filename = os.path.join(savedirs, filename)

        file_data = []
        if os.path.isfile(filename):
            file_data = [i.strip().lower() for i in open(filename) if i]

        try:
            f = codecs.open(filename, 'a', encoding='utf-8', errors='ignore')
            data = '\n{}\n{}\n'.format(name, self.url) if not unsafe else u'\n{}\n{}\n'.format(
                name, self.url)
            if name.lower() not in file_data:
                f.write(data)
        except (OSError, Exception, UnicodeDecodeError) as e:
            retVal = {'status' : 'False', 'msg' : '{}'.format(e)}
        else:
            retVal = {'status' : 'True', 'msg' : 'download'}
            f.close()

        return retVal

    def download(self, filepath="", unsafe=False, quiet=False, callback=lambda *x: None):
        savedir = filename = ""
        retVal = {}

        if filepath and os.path.isdir(filepath):
            savedir, filename = filepath, self.filename if not unsafe else self.unsafe_filename

        elif filepath:
            savedir, filename = os.path.split(filepath)

        else:
            filename = self.filename if not unsafe else self.unsafe_filename

        filepath = os.path.join(savedir, filename)
        if os.name == "nt" and len(filepath) > 250:
            filepath = "\\\\?\\{}".format(filepath)

        if self.mediatype == 'external_link':
            return self._write_external_links(filepath, unsafe)

        if filepath and filepath.endswith('.vtt'):
            filepath_vtt2srt = filepath.replace('.vtt', '.srt')
            if os.path.isfile(filepath_vtt2srt):
                retVal = {"status" : "True", "msg" : "already downloaded"}
                return retVal

        if os.path.isfile(filepath):
            retVal = {"status": "True", "msg": "already downloaded"}
            return retVal

        temp_filepath = filepath + ".part"

        self._active = True
        bytes_to_be_downloaded = 0
        fmode, offset = "wb", 0
        chunksize, bytesdone, t0 = 16384, 0, time.time()
        headers = {'User-Agent': HEADERS.get('User-Agent'), "Accept-Encoding": None}
        if os.path.exists(temp_filepath):
            offset = os.stat(temp_filepath).st_size

        if offset:
            offset_range = 'bytes={}-'.format(offset)
            headers['Range'] = offset_range
            bytesdone = offset
            fmode = "ab"

        status_string = ('  {:,} Bytes [{:.2%}] received. Rate: [{:4.0f} '
                         'KB/s].  ETA: [{:.0f} secs]')

        if early_py_version:
            status_string = ('  {0:} Bytes [{1:.2%}] received. Rate:'
                             ' [{2:4.0f} KB/s].  ETA: [{3:.0f} secs]')

        try:
            try:
                response = self._sess.get(self.url, headers=headers, stream=True, timeout=10)
            except conn_error as error:
                return {'status': 'False', 'msg': 'ConnectionError: %s' % (str(error))}
            if response.ok:
                bytes_to_be_downloaded = total = int(response.headers.get('Content-Length'))
                if bytesdone > 0:
                    bytes_to_be_downloaded = bytes_to_be_downloaded + bytesdone
                total = bytes_to_be_downloaded
                with open(temp_filepath, fmode) as media_file:
                    is_malformed = False
                    for chunk in response.iter_content(chunksize):
                        if not chunk:
                            break
                        media_file.write(chunk)
                        elapsed = time.time() - t0
                        bytesdone += len(chunk)
                        if elapsed:
                            try:
                                rate = ((float(bytesdone) - float(offset)) / 1024.0) / elapsed
                                eta = (total - bytesdone) / (rate * 1024.0)
                            except ZeroDivisionError:
                                is_malformed = True
                                try:
                                    os.unlink(temp_filepath)
                                except Exception:
                                    pass
                                retVal = {"status" : "False", "msg" : "ZeroDivisionError : it seems, lecture has malfunction or is zero byte(s) .."}
                                break
                        else:
                            rate = 0
                            eta = 0

                        if not is_malformed:
                            progress_stats = (
                                bytesdone, bytesdone * 1.0 / total, rate, eta)

                            if not quiet:
                                status = status_string.format(*progress_stats)
                                sys.stdout.write(
                                    "\r" + status + ' ' * 4 + "\r")
                                sys.stdout.flush()

                            if callback:
                                callback(total, *progress_stats)
            if not response.ok:
                code = response.status_code
                reason = response.reason
                retVal = {
                    "status": "False", "msg": "Udemy returned HTTP Code %s: %s" % (code, reason)}
                response.close()
        except KeyboardInterrupt as error:
            raise error
        except Exception as error:
            retVal = {"status": "False",
                      "msg": "Reason : {}".format(str(error))}
            return retVal
        # check if file is downloaded completely
        if os.path.isfile(temp_filepath):
            total_bytes_done = os.stat(temp_filepath).st_size
            if total_bytes_done == bytes_to_be_downloaded:
                self._active = False
            if total_bytes_done < bytes_to_be_downloaded:
                # set active to be True as remaining bytes to be downloaded
                self._active = True
                # try downloading back again remaining bytes until we download completely
                self.download(filepath=filepath,
                              unsafe=unsafe,
                              quiet=quiet)


        if not self._active:
            os.rename(temp_filepath, filepath)
            retVal = {"status": "True", "msg": "download"}

        return retVal

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

        self._mediatype = None
        self._quality = None
        self._resolution = None
        self._dimention = None
        self._extension = None
        self._url = None

        self._parent = parent
        self._filename = None
        self._fsize = None
        self._active = False

        Downloader.__init__(self)

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
    def url(self):
        return self._url

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
    def filename(self):
        if not self._filename:
            self._filename = self._generate_filename()
        return self._filename

    @property
    def title(self):
        return self._parent.title

    @property
    def unsafe_title(self):
        return self._parent.unsafe_title

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
            headers = {'User-Agent': HEADERS.get('User-Agent')}
            try:
                with requests.get(self.url, stream=True, headers=headers) as resp:
                    if resp.ok:
                        self._fsize = float(resp.headers.get('Content-Length', 0))
                    if not resp.ok:
                        self._fsize = 0
            except conn_error:
                self._fsize = 0
        return self._fsize

class UdemyLectureAssets(Downloader):

    def __init__(self, parent):

        self._extension = None
        self._mediatype = None
        self._url = None

        self._parent = parent
        self._filename = None
        self._fsize = None
        self._active = False

        Downloader.__init__(self)

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
            headers = {'User-Agent': HEADERS.get('User-Agent')}
            try:
                with requests.get(self.url, stream=True, headers=headers) as resp:
                    if resp.ok:
                        self._fsize = float(resp.headers.get('Content-Length', 0))
                    if not resp.ok:
                        self._fsize = 0
            except conn_error:
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

        Downloader.__init__(self)

    def __repr__(self):
        out = "%s:%s@%s" % (self.mediatype, self.language, self.extension)
        return out

    def _generate_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.title)
        filename += ".{}.{}".format(self.language, self.extension)
        return filename

    def _generate_unsafe_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.unsafe_title)
        filename += ".{}.{}".format(self.language, self.extension)
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
            headers = {'User-Agent': HEADERS.get('User-Agent')}
            try:
                with requests.get(self.url, stream=True, headers=headers) as resp:
                    if resp.ok:
                        self._fsize = float(resp.headers.get('Content-Length', 0))
                    if not resp.ok:
                        self._fsize = 0
            except conn_error:
                self._fsize = 0
        return self._fsize
