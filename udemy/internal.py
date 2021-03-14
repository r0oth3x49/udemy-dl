# pylint: disable=R,C,W
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from udemy.compat import time, sys
from udemy.logger import logger
from udemy.extract import Udemy
from udemy.shared import (
    UdemyCourse,
    UdemyCourses,
    UdemyChapters,
    UdemyLectures,
    UdemyLectureStream,
    UdemyLectureAssets,
    UdemyLectureSubtitles,
)


class InternUdemyCourses(UdemyCourses, Udemy):
    def __init__(self, *args, **kwargs):
        super(InternUdemyCourses, self).__init__(*args, **kwargs)

    def _fetch_course(self):
        auth = {}
        if not self._cookies:
            auth = self._login(username=self._username, password=self._password)
        if not auth and self._cookies:
            auth = self._login(cookies=self._cookies)
        if auth.get("login") == "successful":
            logger.info(msg="Logged in successfully.", new_line=True)
            logger.info(msg="Fetching all enrolled course(s) url(s)..")
            self._courses = self._extract_subscribed_courses()
            time.sleep(1)
            logger.success(msg="Fetching all enrolled course(s) url(s).. ")
            self._logout()
        if auth.get("login") == "failed":
            logger.error(msg="Failed to login ..\n")
            sys.exit(0)


class InternUdemyCourse(UdemyCourse, Udemy):
    def __init__(self, *args, **kwargs):
        self._info = ""
        super(InternUdemyCourse, self).__init__(*args, **kwargs)

    def _fetch_course(self):
        if self._have_basic:
            return
        auth = {}
        if not self._cookies:
            auth = self._login(
                username=self._username,
                password=self._password,
                cache_session=self._cache_session,
            )
        if not auth and self._cookies:
            auth = self._login(cookies=self._cookies, cache_session=self._cache_session)
        if auth.get("login") == "successful":
            logger.info(msg="Logged in successfully.", new_line=True)
            logger.info(msg="Downloading course information ..")
            self._info = self._real_extract(
                self._url, skip_hls_stream=self._skip_hls_stream
            )
            time.sleep(1)
            logger.success(msg="Downloaded course information .. ")
            access_token = self._info["access_token"]
            self._id = self._info["course_id"]
            self._title = self._info["course_title"]
            self._chapters_count = self._info["total_chapters"]
            self._total_lectures = self._info["total_lectures"]
            self._chapters = [
                InternUdemyChapter(z, access_token=access_token)
                for z in self._info["chapters"]
            ]
            logger.info(
                msg="Trying to logout now...",
                new_line=True,
            )
            if not self._cookies:
                self._logout()
            logger.info(
                msg="Logged out successfully.",
                new_line=True,
            )
            self._have_basic = True
        if auth.get("login") == "failed":
            logger.error(msg="Failed to login ..\n")
            sys.exit(0)


class InternUdemyChapter(UdemyChapters):
    def __init__(self, chapter, access_token=None):
        super(InternUdemyChapter, self).__init__()

        self._chapter_id = chapter["chapter_id"]
        self._chapter_title = chapter["chapter_title"]
        self._chapter_index = chapter["chapter_index"]
        self._lectures_count = chapter.get("lectures_count", 0)
        self._lectures = (
            [
                InternUdemyLecture(z, access_token=access_token)
                for z in chapter["lectures"]
            ]
            if self._lectures_count > 0
            else []
        )


class InternUdemyLecture(UdemyLectures):
    def __init__(self, lectures, access_token=None):
        super(InternUdemyLecture, self).__init__()
        self._access_token = access_token
        self._info = lectures

        self._lecture_id = self._info["lectures_id"]
        self._lecture_title = self._info["lecture_title"]
        self._lecture_index = self._info["lecture_index"]

        self._subtitles_count = self._info.get("subtitle_count", 0)
        self._sources_count = self._info.get("sources_count", 0)
        self._assets_count = self._info.get("assets_count", 0)
        self._extension = self._info.get("extension")
        self._html_content = self._info.get("html_content")
        self._duration = self._info.get("duration")
        if self._duration:
            duration = int(self._duration)
            (mins, secs) = divmod(duration, 60)
            (hours, mins) = divmod(mins, 60)
            if hours == 0:
                self._duration = "%02d:%02d" % (mins, secs)
            else:
                self._duration = "%02d:%02d:%02d" % (hours, mins, secs)

    def _process_streams(self):
        streams = (
            [InternUdemyLectureStream(z, self) for z in self._info["sources"]]
            if self._sources_count > 0
            else []
        )
        self._streams = sorted(streams, key=lambda k: k.quality)
        self._streams = sorted(self._streams, key=lambda k: k.mediatype)

    def _process_assets(self):
        assets = (
            [InternUdemyLectureAssets(z, self) for z in self._info["assets"]]
            if self._assets_count > 0
            else []
        )
        self._assets = assets

    def _process_subtitles(self):
        subtitles = (
            [InternUdemyLectureSubtitles(z, self) for z in self._info["subtitles"]]
            if self._subtitles_count > 0
            else []
        )
        self._subtitles = subtitles


class InternUdemyLectureStream(UdemyLectureStream):
    def __init__(self, sources, parent):
        super(InternUdemyLectureStream, self).__init__(parent)

        self._mediatype = sources.get("type")
        self._extension = sources.get("extension")
        self._token = parent._access_token
        height = sources.get("height", "0")
        width = sources.get("width", "0")
        self._resolution = "%sx%s" % (width, height)
        self._dimension = width, height
        self._quality = int(height)
        self._is_hls = "hls" in self._mediatype
        self._url = sources.get("download_url")


class InternUdemyLectureAssets(UdemyLectureAssets):
    def __init__(self, assets, parent):
        super(InternUdemyLectureAssets, self).__init__(parent)

        self._mediatype = assets.get("type")
        self._extension = assets.get("extension")
        title = assets.get("title", "")
        if not title:
            title = assets.get("filename")
        if title and title.endswith(self._extension):
            ok = "{0:03d} ".format(parent._lecture_index) + title
            self._filename = ok
        else:
            ok = "{0:03d} ".format(parent._lecture_index) + assets.get("filename")
            self._filename = ok
        self._url = assets.get("download_url")


class InternUdemyLectureSubtitles(UdemyLectureSubtitles):
    def __init__(self, subtitles, parent):
        super(InternUdemyLectureSubtitles, self).__init__(parent)

        self._mediatype = subtitles.get("type")
        self._extension = subtitles.get("extension")
        self._language = subtitles.get("language")
        self._url = subtitles.get("download_url")
