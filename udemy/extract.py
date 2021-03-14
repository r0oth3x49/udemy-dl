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


from udemy.auth import UdemyAuth
from udemy.utils import (
    parse_json,
    js_to_json,
    search_regex,
    unescapeHTML,
    extract_cookie_string,
)
from udemy.compat import (
    re,
    sys,
    time,
    m3u8,
    encoding,
    conn_error,
    COURSE_URL,
    MY_COURSES_URL,
    COURSE_SEARCH,
    COLLECTION_URL,
    SUBSCRIBED_COURSES,
)
from udemy.sanitize import slugify, sanitize, SLUG_OK
from udemy.logger import logger
from udemy.getpass import getpass


class Udemy:
    def __init__(self):
        self._session = ""
        self._cookies = ""
        self._access_token = ""

    def _clean(self, text):
        ok = re.compile(r'[^\\/:*?"<>|]')
        text = "".join(x if ok.match(x) else "_" for x in text)
        text = re.sub(r"\.+$", "", text.strip())
        return text

    def _sanitize(self, unsafetext):
        text = sanitize(
            slugify(unsafetext, lower=False, spaces=True, ok=SLUG_OK + "().[]")
        )
        return text

    def _course_name(self, url):
        mobj = re.search(
            r"(?i)(?://(?P<portal_name>.+?).udemy.com/(?:course(/draft)*/)?(?P<name_or_id>[a-zA-Z0-9_-]+))",
            url,
        )
        if mobj:
            return mobj.group("portal_name"), mobj.group("name_or_id")

    def _login(self, username="", password="", cookies="", cache_session=False):
        # check if we already have session on udemy.
        auth = UdemyAuth(cache_session=cache_session)
        is_exists, conf = auth.is_session_exists()
        if is_exists and username and password:
            logger.info(
                msg="Using existing session..",
                new_line=True,
            )
            cookies = conf.get("cookies")
        if not is_exists and not cookies:
            cookies = None
            if not username and not password:
                logger.info(
                    msg="Updating session cookie..",
                    new_line=True,
                )
                username = conf.get("username")
                password = conf.get("password")
            if not username and not password and not cookies:
                print("")
                cookies = getpass.get_access_token(prompt="Access Token : ")
                if not cookies:
                    username = getpass.getuser(prompt="Username : ")
                    password = getpass.getpass(prompt="Password : ")
                print("\n")
                if not cookies and not username and not password:
                    logger.error(
                        msg=f"You should either provide Fresh Access Token or Username/Password to create new udemy session.."
                    )
                    sys.exit(0)
        if not cookies:
            auth.username = username
            auth.password = password
            self._session, self._access_token = auth.authenticate()
        if cookies:
            self._cookies = extract_cookie_string(raw_cookies=cookies)
            self._access_token = self._cookies.get("access_token")
            client_id = self._cookies.get("client_id")
            self._session, _ = auth.authenticate(
                access_token=self._access_token, client_id=client_id
            )
            self._session._session.cookies.update(self._cookies)
        if self._session is not None:
            return {"login": "successful"}
        else:
            return {"login": "failed"}

    def _logout(self):
        """terminates current session if it's based on username/password and keeps the session cookie"""
        return self._session.terminate()

    def _subscribed_courses(self, portal_name, course_name):
        results = []
        self._session._headers.update(
            {
                "Host": "{portal_name}.udemy.com".format(portal_name=portal_name),
                "Referer": "https://{portal_name}.udemy.com/home/my-courses/search/?q={course_name}".format(
                    portal_name=portal_name, course_name=course_name
                ),
            }
        )
        url = COURSE_SEARCH.format(portal_name=portal_name, course_name=course_name)
        try:
            webpage = self._session._get(url).json()
        except conn_error as error:
            logger.error(msg=f"Udemy Says: Connection error, {error}")
            time.sleep(0.8)
            sys.exit(0)
        except (ValueError, Exception) as error:
            logger.error(msg=f"Udemy Says: {error} on {url}")
            time.sleep(0.8)
            sys.exit(0)
        else:
            results = webpage.get("results", [])
        return results

    def _my_courses(self, portal_name):
        results = []
        try:
            url = MY_COURSES_URL.format(portal_name=portal_name)
            webpage = self._session._get(url).json()
        except conn_error as error:
            logger.error(msg=f"Udemy Says: Connection error, {error}")
            time.sleep(0.8)
            sys.exit(0)
        except (ValueError, Exception) as error:
            logger.error(msg=f"Udemy Says: {error}")
            time.sleep(0.8)
            sys.exit(0)
        else:
            results = webpage.get("results", [])
        return results

    def _archived_courses(self, portal_name):
        results = []
        try:
            url = MY_COURSES_URL.format(portal_name=portal_name)
            url = f"{url}&is_archived=true"
            webpage = self._session._get(url).json()
        except conn_error as error:
            logger.error(msg=f"Udemy Says: Connection error, {error}")
            time.sleep(0.8)
            sys.exit(0)
        except (ValueError, Exception) as error:
            logger.error(msg=f"Udemy Says: {error}")
            time.sleep(0.8)
            sys.exit(0)
        else:
            results = webpage.get("results", [])
        return results

    def _subscribed_collection_courses(self, portal_name):
        url = COLLECTION_URL.format(portal_name=portal_name)
        courses_lists = []
        try:
            webpage = self._session._get(url).json()
        except conn_error as error:
            logger.error(msg=f"Udemy Says: Connection error, {error}")
            time.sleep(0.8)
            sys.exit(0)
        except (ValueError, Exception) as error:
            logger.error(msg=f"Udemy Says: {error}")
            time.sleep(0.8)
            sys.exit(0)
        else:
            results = webpage.get("results", [])
            if results:
                [
                    courses_lists.extend(courses.get("courses", []))
                    for courses in results
                    if courses.get("courses", [])
                ]
        return courses_lists

    def _extract_subscribed_courses(self):
        def clean_urls(courses):
            _urls = []
            courses = [
                dict(tupleized)
                for tupleized in set(tuple(item.items()) for item in courses)
            ]
            for entry in courses:
                logger.progress(msg="Fetching all enrolled course(s) url(s).. ")
                url = entry.get("url")
                if not url:
                    continue
                url = f"https://www.udemy.com{url}"
                _urls.append(url)
            _urls = list(set(_urls))
            return _urls

        _temp = []
        try:
            response = self._session._get(SUBSCRIBED_COURSES).json()
        except conn_error as error:
            logger.error(msg=f"Udemy Says: Connection error, {error}")
            time.sleep(0.8)
            sys.exit(0)
        except (ValueError, Exception) as error:
            logger.error(msg=f"Udemy Says: {error}")
            time.sleep(0.8)
            sys.exit(0)
        else:
            results = response.get("results", [])
            _temp.extend(results)
            _next = response.get("next")
            logger.progress(msg="Fetching all enrolled course(s) url(s).. ")
            while _next:
                logger.progress(msg="Fetching all enrolled course(s) url(s).. ")
                try:
                    resp = self._session._get(_next)
                    resp.raise_for_status()
                    resp = resp.json()
                except conn_error as error:
                    logger.error(msg=f"Udemy Says: Connection error, {error}")
                    time.sleep(0.8)
                    sys.exit(0)
                except Exception as error:
                    logger.error(msg=f"Udemy Says: error, {error}")
                    time.sleep(0.8)
                    sys.exit(0)
                else:
                    _next = resp.get("next")
                    results = resp.get("results", [])
                    _temp.extend(results)
        if _temp:
            _temp = clean_urls(_temp)
        return _temp

    def __extract_course(self, response, course_name):
        _temp = {}
        if response:
            for entry in response:
                course_id = str(entry.get("id"))
                published_title = entry.get("published_title")
                if course_name in (published_title, course_id):
                    _temp = entry
                    break
        return _temp

    def _extract_course_info(self, url):
        portal_name, course_name = self._course_name(url)
        course = {}
        results = self._subscribed_courses(
            portal_name=portal_name, course_name=course_name
        )
        course = self.__extract_course(response=results, course_name=course_name)
        if not course:
            results = self._my_courses(portal_name=portal_name)
            course = self.__extract_course(response=results, course_name=course_name)
        if not course:
            results = self._subscribed_collection_courses(portal_name=portal_name)
            course = self.__extract_course(response=results, course_name=course_name)
        if not course:
            results = self._archived_courses(portal_name=portal_name)
            course = self.__extract_course(response=results, course_name=course_name)

        if course:
            course.update({"portal_name": portal_name})
            return course.get("id"), course
        if not course:
            logger.failed(msg="Downloading course information, course id not found .. ")
            logger.info(
                msg="It seems either you are not enrolled or you have to visit the course atleast once while you are logged in.",
                new_line=True,
            )
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
            sys.exit(0)

    def _extract_large_course_content(self, url):
        url = url.replace("10000", "50") if url.endswith("10000") else url
        try:
            data = self._session._get(url).json()
        except conn_error as error:
            logger.error(msg=f"Udemy Says: Connection error, {error}")
            time.sleep(0.8)
            sys.exit(0)
        else:
            _next = data.get("next")
            while _next:
                logger.progress(msg="Downloading course information .. ")
                try:
                    resp = self._session._get(_next).json()
                except conn_error as error:
                    logger.error(msg=f"Udemy Says: Connection error, {error}")
                    time.sleep(0.8)
                    sys.exit(0)
                else:
                    _next = resp.get("next")
                    results = resp.get("results")
                    if results and isinstance(results, list):
                        for d in resp["results"]:
                            data["results"].append(d)
            return data

    def _extract_course_json(self, url, course_id, portal_name):
        self._session._headers.update({"Referer": url})
        url = COURSE_URL.format(portal_name=portal_name, course_id=course_id)
        try:
            resp = self._session._get(url)
            if resp.status_code in [502, 503]:
                resp = self._extract_large_course_content(url=url)
            else:
                resp = resp.json()
        except conn_error as error:
            logger.error(msg=f"Udemy Says: Connection error, {error}")
            time.sleep(0.8)
            sys.exit(0)
        except (ValueError, Exception):
            resp = self._extract_large_course_content(url=url)
            return resp
        else:
            return resp

    def _html_to_json(self, view_html, lecture_id):
        data = parse_json(
            search_regex(
                r'videojs-setup-data=(["\'])(?P<data>{.+?})\1',
                view_html,
                "setup data",
                default="{}",
                group="data",
            ),
            lecture_id,
            transform_source=unescapeHTML,
            fatal=False,
        )
        text_tracks = parse_json(
            search_regex(
                r'text-tracks=(["\'])(?P<data>\[.+?\])\1',
                view_html,
                "text tracks",
                default="{}",
                group="data",
            ),
            lecture_id,
            transform_source=lambda s: js_to_json(unescapeHTML(s)),
            fatal=False,
        )
        return data, text_tracks

    def _extract_m3u8(self, url):
        """extracts m3u8 streams"""
        _temp = []
        try:
            resp = self._session._get(url)
            resp.raise_for_status()
            raw_data = resp.text
            m3u8_object = m3u8.loads(raw_data)
            playlists = m3u8_object.playlists
            seen = set()
            for pl in playlists:
                resolution = pl.stream_info.resolution
                codecs = pl.stream_info.codecs
                if not resolution:
                    continue
                if not codecs:
                    continue
                width, height = resolution
                download_url = pl.uri
                if height not in seen:
                    seen.add(height)
                    _temp.append(
                        {
                            "type": "hls",
                            "height": str(height),
                            "width": str(width),
                            "extension": "mp4",
                            "download_url": download_url,
                        }
                    )
        except Exception as error:
            logger.error(msg=f"Udemy Says : '{error}' while fetching hls streams..")
        return _temp

    def _extract_ppt(self, assets):
        _temp = []
        download_urls = assets.get("download_urls")
        filename = assets.get("filename")
        if download_urls and isinstance(download_urls, dict):
            extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
            download_url = download_urls.get("Presentation", [])[0].get("file")
            _temp.append(
                {
                    "type": "presentation",
                    "filename": filename,
                    "extension": extension,
                    "download_url": download_url,
                }
            )
        return _temp

    def _extract_file(self, assets):
        _temp = []
        download_urls = assets.get("download_urls")
        filename = assets.get("filename")
        if download_urls and isinstance(download_urls, dict):
            extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
            download_url = download_urls.get("File", [])[0].get("file")
            _temp.append(
                {
                    "type": "file",
                    "filename": filename,
                    "extension": extension,
                    "download_url": download_url,
                }
            )
        return _temp

    def _extract_ebook(self, assets):
        _temp = []
        download_urls = assets.get("download_urls")
        filename = assets.get("filename")
        if download_urls and isinstance(download_urls, dict):
            extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
            download_url = download_urls.get("E-Book", [])[0].get("file")
            _temp.append(
                {
                    "type": "ebook",
                    "filename": filename,
                    "extension": extension,
                    "download_url": download_url,
                }
            )
        return _temp

    def _extract_audio(self, assets):
        _temp = []
        download_urls = assets.get("download_urls")
        filename = assets.get("filename")
        if download_urls and isinstance(download_urls, dict):
            extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
            download_url = download_urls.get("Audio", [])[0].get("file")
            _temp.append(
                {
                    "type": "audio",
                    "filename": filename,
                    "extension": extension,
                    "download_url": download_url,
                }
            )
        return _temp

    def _extract_sources(self, sources, skip_hls_stream=False):
        _temp = []
        if sources and isinstance(sources, list):
            for source in sources:
                label = source.get("label")
                download_url = source.get("file")
                if not download_url:
                    continue
                if label.lower() == "audio":
                    continue
                height = label if label else None
                if height == "2160":
                    width = "3840"
                elif height == "1440":
                    width = "2560"
                elif height == "1080":
                    width = "1920"
                elif height == "720":
                    width = "1280"
                elif height == "480":
                    width = "854"
                elif height == "360":
                    width = "640"
                elif height == "240":
                    width = "426"
                else:
                    width = "256"
                if (
                    source.get("type") == "application/x-mpegURL"
                    or "m3u8" in download_url
                ):
                    if not skip_hls_stream:
                        out = self._extract_m3u8(download_url)
                        if out:
                            _temp.extend(out)
                else:
                    _type = source.get("type")
                    _temp.append(
                        {
                            "type": "video",
                            "height": height,
                            "width": width,
                            "extension": _type.replace("video/", ""),
                            "download_url": download_url,
                        }
                    )
        return _temp

    def _extract_subtitles(self, tracks):
        _temp = []
        if tracks and isinstance(tracks, list):
            for track in tracks:
                if not isinstance(track, dict):
                    continue
                if track.get("_class") != "caption":
                    continue
                download_url = track.get("url")
                if not download_url or not isinstance(download_url, encoding):
                    continue
                lang = (
                    track.get("language")
                    or track.get("srclang")
                    or track.get("label")
                    or track["locale_id"].split("_")[0]
                )
                ext = "vtt" if "vtt" in download_url.rsplit(".", 1)[-1] else "srt"
                _temp.append(
                    {
                        "type": "subtitle",
                        "language": lang,
                        "extension": ext,
                        "download_url": download_url,
                    }
                )
        return _temp

    def _extract_supplementary_assets(self, supp_assets):
        _temp = []
        for entry in supp_assets:
            title = self._clean(entry.get("title"))
            filename = entry.get("filename")
            download_urls = entry.get("download_urls")
            external_url = entry.get("external_url")
            asset_type = entry.get("asset_type").lower()
            if asset_type == "file":
                if download_urls and isinstance(download_urls, dict):
                    extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
                    download_url = download_urls.get("File", [])[0].get("file")
                    _temp.append(
                        {
                            "type": "file",
                            "title": title,
                            "filename": filename,
                            "extension": extension,
                            "download_url": download_url,
                        }
                    )
            elif asset_type == "sourcecode":
                if download_urls and isinstance(download_urls, dict):
                    extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
                    download_url = download_urls.get("SourceCode", [])[0].get("file")
                    _temp.append(
                        {
                            "type": "source_code",
                            "title": title,
                            "filename": filename,
                            "extension": extension,
                            "download_url": download_url,
                        }
                    )
            elif asset_type == "externallink":
                _temp.append(
                    {
                        "type": "external_link",
                        "title": title,
                        "filename": filename,
                        "extension": "txt",
                        "download_url": external_url,
                    }
                )
        return _temp

    def _real_extract(self, url="", skip_hls_stream=False):

        _udemy = {}
        course_id, course_info = self._extract_course_info(url)

        if course_info and isinstance(course_info, dict):
            title = self._clean(course_info.get("title"))
            course_title = course_info.get("published_title")
            portal_name = course_info.get("portal_name")

        course_json = self._extract_course_json(url, course_id, portal_name)
        course = course_json.get("results")
        resource = course_json.get("detail")

        if resource:
            if not self._cookies:
                logger.error(
                    msg=f"Udemy Says : '{resource}' Run udemy-dl against course within few seconds"
                )
            if self._cookies:
                logger.error(
                    msg=f"Udemy Says : '{resource}' cookies seems to be expired"
                )
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
            sys.exit(0)

        _udemy["access_token"] = self._access_token
        _udemy["course_id"] = course_id
        _udemy["title"] = title
        _udemy["course_title"] = course_title
        _udemy["chapters"] = []

        counter = -1

        if course:
            lecture_counter = 0
            for entry in course:
                clazz = entry.get("_class")
                asset = entry.get("asset")
                supp_assets = entry.get("supplementary_assets")

                if clazz == "chapter":
                    lecture_counter = 0
                    lectures = []
                    chapter_index = entry.get("object_index")
                    chapter_title = "{0:02d} ".format(chapter_index) + self._clean(
                        entry.get("title")
                    )
                    if chapter_title not in _udemy["chapters"]:
                        _udemy["chapters"].append(
                            {
                                "chapter_title": chapter_title,
                                "chapter_id": entry.get("id"),
                                "chapter_index": chapter_index,
                                "lectures": [],
                            }
                        )
                        counter += 1
                elif clazz == "lecture":
                    lecture_counter += 1
                    lecture_id = entry.get("id")
                    if len(_udemy["chapters"]) == 0:
                        lectures = []
                        chapter_index = entry.get("object_index")
                        chapter_title = "{0:02d} ".format(chapter_index) + self._clean(
                            entry.get("title")
                        )
                        if chapter_title not in _udemy["chapters"]:
                            _udemy["chapters"].append(
                                {
                                    "chapter_title": chapter_title,
                                    "chapter_id": lecture_id,
                                    "chapter_index": chapter_index,
                                    "lectures": [],
                                }
                            )
                            counter += 1

                    if lecture_id:

                        retVal = []

                        if isinstance(asset, dict):
                            asset_type = (
                                asset.get("asset_type").lower()
                                or asset.get("assetType").lower()
                            )
                            if asset_type == "article":
                                if (
                                    isinstance(supp_assets, list)
                                    and len(supp_assets) > 0
                                ):
                                    retVal = self._extract_supplementary_assets(
                                        supp_assets
                                    )
                            elif asset_type == "video":
                                if (
                                    isinstance(supp_assets, list)
                                    and len(supp_assets) > 0
                                ):
                                    retVal = self._extract_supplementary_assets(
                                        supp_assets
                                    )
                            elif asset_type == "e-book":
                                retVal = self._extract_ebook(asset)
                            elif asset_type == "file":
                                retVal = self._extract_file(asset)
                            elif asset_type == "presentation":
                                retVal = self._extract_ppt(asset)
                            elif asset_type == "audio":
                                retVal = self._extract_audio(asset)

                        logger.progress(msg="Downloading course information .. ")
                        lecture_index = entry.get("object_index")
                        lecture_title = "{0:03d} ".format(
                            lecture_counter
                        ) + self._clean(entry.get("title"))
                        data = asset.get("stream_urls")
                        if data and isinstance(data, dict):
                            sources = data.get("Video")
                            tracks = asset.get("captions")
                            duration = asset.get("time_estimation")
                            sources = self._extract_sources(
                                sources, skip_hls_stream=skip_hls_stream
                            )
                            subtitles = self._extract_subtitles(tracks)
                            sources_count = len(sources)
                            subtitle_count = len(subtitles)
                            lectures.append(
                                {
                                    "index": lecture_counter,
                                    "lecture_index": lecture_index,
                                    "lectures_id": lecture_id,
                                    "lecture_title": lecture_title,
                                    "duration": duration,
                                    "assets": retVal,
                                    "assets_count": len(retVal),
                                    "sources": sources,
                                    "subtitles": subtitles,
                                    "subtitle_count": subtitle_count,
                                    "sources_count": sources_count,
                                }
                            )
                        else:
                            lectures.append(
                                {
                                    "index": lecture_counter,
                                    "lecture_index": lecture_index,
                                    "lectures_id": lecture_id,
                                    "lecture_title": lecture_title,
                                    "html_content": asset.get("body"),
                                    "extension": "html",
                                    "assets": retVal,
                                    "assets_count": len(retVal),
                                    "subtitle_count": 0,
                                    "sources_count": 0,
                                }
                            )

                    _udemy["chapters"][counter]["lectures"] = lectures
                    _udemy["chapters"][counter]["lectures_count"] = len(lectures)
                elif clazz == "quiz":
                    lecture_id = entry.get("id")
                    if len(_udemy["chapters"]) == 0:
                        lectures = []
                        chapter_index = entry.get("object_index")
                        chapter_title = "{0:02d} ".format(chapter_index) + self._clean(
                            entry.get("title")
                        )
                        if chapter_title not in _udemy["chapters"]:
                            lecture_counter = 0
                            _udemy["chapters"].append(
                                {
                                    "chapter_title": chapter_title,
                                    "chapter_id": lecture_id,
                                    "chapter_index": chapter_index,
                                    "lectures": [],
                                }
                            )
                            counter += 1
                    _udemy["chapters"][counter]["lectures"] = lectures
                    _udemy["chapters"][counter]["lectures_count"] = len(lectures)
            _udemy["total_chapters"] = len(_udemy["chapters"])
            _udemy["total_lectures"] = sum(
                [
                    entry.get("lectures_count", 0)
                    for entry in _udemy["chapters"]
                    if entry
                ]
            )

        return _udemy
