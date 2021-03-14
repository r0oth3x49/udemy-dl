# pylint: disable=R,C
#!/usr/bin/env python3

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
    time,
    requests,
    conn_error,
    HEADERS,
)
from udemy.ffmpeg import FFMPeg
from udemy.utils import to_file, prepare_html


class Downloader(object):
    def __init__(self):
        self._url = None
        self._filename = None
        self._mediatype = None
        self._extension = None
        self._active = True
        self._is_hls = False
        self._token = None
        self._sess = requests.session()

    @property
    def url(self):
        """abac"""
        return self._url

    @property
    def token(self):
        return self._token

    @property
    def is_hls(self):
        return self._is_hls

    @property
    def mediatype(self):
        return self._mediatype

    @property
    def extension(self):
        return self._extension

    @property
    def filename(self):
        if not self._filename:
            self._filename = self._generate_filename()  # pylint: disable=E
        return self._filename

    def _generate_filename():  # pylint: disable=E
        pass

    def _write_external_links(self, filepath):
        retVal = {}
        savedirs, name = os.path.split(filepath)
        filename = u"external-assets-links.txt"
        filename = os.path.join(savedirs, filename)
        file_data = []
        if os.path.isfile(filename):
            file_data = [
                i.strip().lower()
                for i in open(filename, encoding="utf-8", errors="ignore")
                if i
            ]

        content = u"\n{}\n{}\n".format(name, self.url)
        if name.lower() not in file_data:
            retVal = to_file(filename, "a", content)
        return retVal

    def download(
        self,
        filepath="",
        quiet=False,
        callback=lambda *x: None,
    ):
        savedir = filename = ""
        retVal = {}

        if filepath and os.path.isdir(filepath):
            savedir, filename = (
                filepath,
                self.filename,
            )

        elif filepath:
            savedir, filename = os.path.split(filepath)

        else:
            filename = self.filename

        filepath = os.path.join(savedir, filename)
        if os.name == "nt" and len(filepath) > 250:
            filepath = "\\\\?\\{}".format(filepath)

        if self.mediatype == "external_link":
            return self._write_external_links(filepath)

        if filepath and filepath.endswith(".vtt"):
            filepath_vtt2srt = filepath.replace(".vtt", ".srt")
            if os.path.isfile(filepath_vtt2srt):
                retVal = {"status": "True", "msg": "already downloaded"}
                return retVal

        if os.path.isfile(filepath):
            retVal = {"status": "True", "msg": "already downloaded"}
            return retVal

        temp_filepath = filepath + ".part"

        if self.is_hls:
            temp_filepath = filepath.replace(".mp4", "")
            temp_filepath = temp_filepath + ".hls-part.mp4"
            retVal = FFMPeg(None, self.url, self.token, temp_filepath).download()
            if retVal:
                self._active = False
        else:
            bytes_to_be_downloaded = 0
            fmode, offset = "wb", 0
            chunksize, bytesdone, t0 = 16384, 0, time.time()
            headers = {"User-Agent": HEADERS.get("User-Agent"), "Accept-Encoding": None}
            if os.path.exists(temp_filepath):
                offset = os.stat(temp_filepath).st_size

            if offset:
                offset_range = "bytes={}-".format(offset)
                headers["Range"] = offset_range
                bytesdone = offset
                fmode = "ab"

            status_string = (
                "  {:,} Bytes [{:.2%}] received. Rate: [{:4.0f} "
                "KB/s].  ETA: [{:.0f} secs]"
            )

            try:
                try:
                    response = self._sess.get(
                        self.url, headers=headers, stream=True, timeout=10
                    )
                except conn_error as error:
                    return {
                        "status": "False",
                        "msg": "ConnectionError: %s" % (str(error)),
                    }
                if response.ok:
                    bytes_to_be_downloaded = total = int(
                        response.headers.get("Content-Length")
                    )
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
                                    rate = (
                                        (float(bytesdone) - float(offset)) / 1024.0
                                    ) / elapsed
                                    eta = (total - bytesdone) / (rate * 1024.0)
                                except ZeroDivisionError:
                                    is_malformed = True
                                    try:
                                        os.unlink(temp_filepath)
                                    except Exception:  # pylint: disable=W
                                        pass
                                    retVal = {
                                        "status": "False",
                                        "msg": "ZeroDivisionError : it seems, lecture has malfunction or is zero byte(s) ..",
                                    }
                                    break
                            else:
                                rate = 0
                                eta = 0

                            if not is_malformed:
                                progress_stats = (
                                    bytesdone,
                                    bytesdone * 1.0 / total,
                                    rate,
                                    eta,
                                )

                                if not quiet:
                                    status = status_string.format(*progress_stats)
                                    sys.stdout.write("\r" + status + " " * 4 + "\r")
                                    sys.stdout.flush()

                                if callback:
                                    callback(total, *progress_stats)
                if not response.ok:
                    code = response.status_code
                    reason = response.reason
                    retVal = {
                        "status": "False",
                        "msg": "Udemy returned HTTP Code %s: %s" % (code, reason),
                    }
                    response.close()
            except KeyboardInterrupt as error:
                raise error
            except Exception as error:  # pylint: disable=W
                retVal = {"status": "False", "msg": "Reason : {}".format(str(error))}
                return retVal
            # # check if file is downloaded completely
            if os.path.isfile(temp_filepath):
                total_bytes_done = os.stat(temp_filepath).st_size
                if total_bytes_done == bytes_to_be_downloaded:
                    self._active = False
                # if total_bytes_done < bytes_to_be_downloaded:
                #     # set active to be True as remaining bytes to be downloaded
                #     self._active = True
                #     # try downloading back again remaining bytes until we download completely
                #     self.download(filepath=filepath, quiet=quiet)

        if not self._active:
            os.rename(temp_filepath, filepath)
            retVal = {"status": "True", "msg": "download"}

        return retVal


class UdemyCourses(object):
    def __init__(self, username="", password="", cookies="", basic=True):

        self._courses = []
        self._username = username
        self._password = password
        self._cookies = cookies

        if basic:
            self._fetch_course()

    def _fetch_course(self):
        raise NotImplementedError

    def dump_courses(self, filepath):
        if not filepath:
            filepath = os.path.join(os.getcwd(), "enrolled-courses.txt")
        with open(filepath, "w") as fd:
            courses_urls = "\n".join(self._courses)
            fd.write(courses_urls)
        return filepath

    @property
    def courses(self):
        return self._courses


class UdemyCourse(object):
    def __init__(
        self,
        url,
        username="",
        password="",
        cookies="",
        basic=True,
        skip_hls_stream=False,
        cache_session=False,
        callback=None,
    ):

        self._url = url
        self._username = username
        self._password = password
        self._cookies = cookies
        self._cache_session = cache_session
        self._skip_hls_stream = skip_hls_stream
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

    def get_chapters(self, chapter_number=None, chapter_start=None, chapter_end=None):
        if not self._chapters:
            self._fetch_course()
        if (
            chapter_number
            and not chapter_start
            and not chapter_end
            and isinstance(chapter_number, int)
        ):
            is_okay = bool(0 < chapter_number <= self.chapters)
            if is_okay:
                self._chapters = [self._chapters[chapter_number - 1]]
        if chapter_start and not chapter_number and isinstance(chapter_start, int):
            is_okay = bool(0 < chapter_start <= self.chapters)
            if is_okay:
                self._chapters = self._chapters[chapter_start - 1 :]
        if chapter_end and not chapter_number and isinstance(chapter_end, int):
            is_okay = bool(0 < chapter_end <= self.chapters)
            if is_okay:
                self._chapters = self._chapters[: chapter_end - 1]
        return self._chapters


class UdemyChapters(object):
    def __init__(self):

        self._chapter_id = None
        self._chapter_index = None
        self._chapter_title = None
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
    def lectures(self):
        return self._lectures_count

    def get_lectures(self, lecture_number=None, lecture_start=None, lecture_end=None):
        if (
            lecture_number
            and not lecture_start
            and not lecture_end
            and isinstance(lecture_number, int)
        ):
            is_okay = bool(0 < lecture_number <= self.lectures)
            if is_okay:
                self._lectures = [self._lectures[lecture_number - 1]]
        if lecture_start and not lecture_number and isinstance(lecture_start, int):
            is_okay = bool(0 < lecture_start <= self.lectures)
            if is_okay:
                self._lectures = self._lectures[lecture_start - 1 :]
        if lecture_end and not lecture_number and isinstance(lecture_end, int):
            is_okay = bool(0 < lecture_end <= self.lectures)
            if is_okay:
                self._lectures = self._lectures[: lecture_end - 1]
        return self._lectures


class UdemyLectures(object):
    def __init__(self):

        self._best = None
        self._duration = None
        self._extension = None
        self._lecture_id = None
        self._lecture_title = None
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
            self._process_assets()  # pylint: disable=E
        return self._assets

    @property
    def streams(self):
        if not self._streams:
            self._process_streams()  # pylint: disable=E
        return self._streams

    @property
    def subtitles(self):
        if not self._subtitles:
            self._process_subtitles()  # pylint: disable=E
        return self._subtitles

    def _getbest(self):
        streams = self.streams
        if not streams:
            return None

        def _sortkey(x, keyres=0, keyftype=0):
            keyres = int(x.resolution.split("x")[0])
            keyftype = x.extension
            st = (keyftype, keyres)
            return st

        self._best = max([i for i in streams if not i.is_hls], key=_sortkey)
        return self._best

    def getbest(self):
        return self._getbest()

    def dump(self, filepath):
        retVal = {}
        filename = os.path.join(filepath, self.title)
        filename += ".html"

        if os.path.isfile(filename):
            retVal = {"status": "True", "msg": "already downloaded"}
            return retVal
        contents = prepare_html(self.title, self.html)
        retVal = to_file(filename, "wb", contents, None, None)
        return retVal


class UdemyLectureStream(Downloader):
    def __init__(self, parent):

        self._mediatype = None
        self._quality = None
        self._resolution = None
        self._dimension = None
        self._extension = None
        self._url = None

        self._parent = parent
        self._filename = None
        self._fsize = None
        self._active = False
        self._is_hls = False
        self._token = None

        Downloader.__init__(self)

    def __repr__(self):
        out = "%s:%s@%s" % (self.mediatype, self.extension, self.quality)
        return out

    def _generate_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.title)
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
    def is_hls(self):
        return self._is_hls

    @property
    def token(self):
        return self._token

    @property
    def id(self):
        return self._parent.id

    @property
    def dimension(self):
        return self._dimension

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
    def mediatype(self):
        return self._mediatype

    def get_quality(self, quality, preferred_mediatype="video"):
        lecture = self._parent.getbest()
        _temp = {}
        for s in self._parent.streams:
            if isinstance(quality, int) and s.quality == quality:
                mediatype = s.mediatype
                _temp[mediatype] = s
        if _temp:
            if preferred_mediatype in _temp:
                lecture = _temp[preferred_mediatype]
            else:
                lecture = list(_temp.values()).pop()
        return lecture

    def get_filesize(self):
        if not self._fsize:
            headers = {"User-Agent": HEADERS.get("User-Agent")}
            try:
                with requests.get(self.url, stream=True, headers=headers) as resp:
                    if resp.ok:
                        self._fsize = float(resp.headers.get("Content-Length", 0))
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
    def filename(self):
        if not self._filename:
            self._filename = self._generate_filename()
        return self._filename

    @property
    def mediatype(self):
        return self._mediatype

    def get_filesize(self):
        if not self._fsize:
            headers = {"User-Agent": HEADERS.get("User-Agent")}
            try:
                with requests.get(self.url, stream=True, headers=headers) as resp:
                    if resp.ok:
                        self._fsize = float(resp.headers.get("Content-Length", 0))
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
    def filename(self):
        if not self._filename:
            self._filename = self._generate_filename()
        return self._filename

    @property
    def mediatype(self):
        return self._mediatype

    def get_subtitle(self, language, preferred_language="en"):
        _temp = {}
        subtitles = self._parent.subtitles
        for sub in subtitles:
            if sub.language == language:
                _temp[sub.language] = [sub]
        if _temp:
            # few checks to keep things simple :D
            if language in _temp:
                _temp = _temp[language]
            elif preferred_language in _temp and not language in _temp:
                _temp = _temp[preferred_language]
        if not _temp:
            _temp = subtitles
        return _temp

    def get_filesize(self):
        if not self._fsize:
            headers = {"User-Agent": HEADERS.get("User-Agent")}
            try:
                with requests.get(self.url, stream=True, headers=headers) as resp:
                    if resp.ok:
                        self._fsize = float(resp.headers.get("Content-Length", 0))
                    if not resp.ok:
                        self._fsize = 0
            except conn_error:
                self._fsize = 0
        return self._fsize
