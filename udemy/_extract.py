#!/usr/bin/python
# -*- coding: utf-8 -*-

'''

Author  : Nasir Khan (r0ot h3x49)
Github  : https://github.com/r0oth3x49
License : MIT


Copyright (c) 2018 Nasir Khan (r0ot h3x49)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH 
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import os
import re
import sys
import json

from pprint  import  pprint
from ._auth  import  UdemyAuth
from ._utils import (
            parse_json,
            js_to_json,
            search_regex,
            unescapeHTML
            )
from ._compat import (
            re,
            time,
            encoding,
            conn_error,
            COURSE_URL,
            ParseCookie,
            MY_COURSES_URL,
            )
from ._sanitize import (
            slugify,
            sanitize,
            SLUG_OK
            )
from ._colorized import *
from ._progress import ProgressBar


class Udemy(ProgressBar):

    def __init__(self):
        self._session = ''
        self._cookies = ''


    def _clean(self, text):
        ok = re.compile(r'[^\\/:*?"<>|]')
        text = "".join(x if ok.match(x) else "_" for x in text)
        return re.sub('\.+$', '', text.rstrip()) if text.endswith(".") else text.rstrip()

    def _course_name(self, url):
        mobj = re.search(r'(?x)(?:(.+)\.com/(?P<course_name>[a-zA-Z0-9_-]+))/', url, re.I)
        if mobj:
            return mobj.group('course_name')

    def _extract_cookie_string(self, raw_cookies):
        cookies = {}
        cookie_parser = ParseCookie()
        try:
            cookie_string = re.search(r'Cookie:\s*(.+)\n', raw_cookies, flags=re.I).group(1)
        except:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Cookies error, Request Headers is required.\n")
            sys.stdout.write(fc + sd + "[" + fm + sb + "i" + fc + sd + "] : " + fg + sb + "Copy Request Headers for single request to a file, while you are logged in.\n")
            sys.exit(0)
        cookie_parser.load(cookie_string)
        for key, cookie in cookie_parser.items():
            cookies[key] = cookie.value
        return cookies

    
    def _sanitize(self, unsafetext):
        text = sanitize(slugify(unsafetext, lower=False, spaces=True, ok=SLUG_OK + '().[]'))
        return text

    def _login(self, username='', password='', cookies=''):
        if not cookies:
            auth = UdemyAuth(username=username, password=password)
            self._session = auth.authenticate()
        if cookies:
            self._cookies = self._extract_cookie_string(raw_cookies=cookies)
            access_token = self._cookies.get('access_token')
            client_id = self._cookies.get('client_id')
            time.sleep(0.3)
            auth = UdemyAuth()
            self._session = auth.authenticate(access_token=access_token, client_id=client_id)
            self._session._session.cookies.update(self._cookies)
        if self._session is not None:
            return {'login' : 'successful'}
        else:
            return {'login' : 'failed'}
    
    def _logout(self):
        return self._session.terminate()

    def _extract_course_info(self, url):
        if 'www' not in url:
            self._session._headers['Host'] = url.replace("https://", "").split('/', 1)[0]
            self._session._headers['Referer'] = url
        try:
            webpage = self._session._get(url).text
        except conn_error as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
            time.sleep(0.8)
            sys.exit(0)
        else:
            course = parse_json(
                        search_regex(
                            r'ng-init=["\'].*\bcourse=({.+?});', 
                            webpage, 
                            'course', 
                            default='{}'
                            ),
                        "Course Information",
                        transform_source=unescapeHTML,
                        fatal=False,
                        )
            course_id = course.get('id') or search_regex(
                                                (r'data-course-id=["\'](\d+)', r'&quot;id&quot;\s*:\s*(\d+)'),
                                                webpage, 
                                                'course id'
                                                )
        if course_id:
            return course_id, course
        else:
            sys.exit(0)

    def _extract_large_course_content(self, url):
        url = url.replace('10000', '300') if url.endswith('10000') else url
        try:
            data = self._session._get(url).json()
        except conn_error as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
            time.sleep(0.8)
            sys.exit(0)
        else:
            _next = data.get('next')
            while _next:
                try:
                    resp = self._session._get(_next).json()
                except conn_error as e:
                    sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
                    time.sleep(0.8)
                    sys.exit(0)
                else:
                    _next = resp.get('next')
                    results = resp.get('results')
                    if results and isinstance(results, list):
                        for d in resp['results']:
                            data['results'].append(d)
            return data

    def _extract_course_json(self, course_id):
        url = COURSE_URL.format(course_id=course_id)
        try:
            resp = self._session._get(url).json()
        except conn_error as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
            time.sleep(0.8)
            sys.exit(0)
        except Exception as e:
            resp = self._extract_large_course_content(url=url)
            return resp
        else:
            return resp

    def _html_to_json(self, view_html, lecture_id):
        data = parse_json(
                    search_regex(
                        r'videojs-setup-data=(["\'])(?P<data>{.+?})\1',
                        view_html,
                        'setup data',
                        default='{}',
                        group='data'),
                    lecture_id,
                    transform_source=unescapeHTML,
                    fatal=False
                    )
        text_tracks = parse_json(
                        search_regex(
                            r'text-tracks=(["\'])(?P<data>\[.+?\])\1',
                            view_html,
                            'text tracks',
                            default='{}',
                            group='data'),
                        lecture_id,
                        transform_source=lambda s: js_to_json(unescapeHTML(s)),
                        fatal=False
                        )
        return data, text_tracks

    def _extract_ppt(self, assets):
        _temp = []
        download_urls = assets.get('download_urls')
        slides_urls = assets.get('slide_urls')
        filename = self._sanitize(assets.get('filename'))
        if download_urls and isinstance(download_urls, dict):
            extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
            download_url = download_urls.get('Presentation', [])[0].get('file')
            _temp.append({
                'type'          :   'presentation',
                'filename'      :   filename,
                'extension'     :   extension,
                'download_url'  :   download_url
                })
        return _temp

    def _extract_file(self, assets):
        _temp = []
        download_urls = assets.get('download_urls')
        filename = self._sanitize(assets.get('filename'))
        if download_urls and isinstance(download_urls, dict):
            extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
            download_url = download_urls.get('File', [])[0].get('file')
            _temp.append({
                'type' : 'file',
                'filename' : filename,
                'extension' : extension,
                'download_url' : download_url
                })
        return _temp

    def _extract_ebook(self, assets):
        _temp = []
        download_urls = assets.get('download_urls')
        filename = self._sanitize(assets.get('filename'))
        if download_urls and isinstance(download_urls, dict):
            extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
            download_url = download_urls.get('E-Book', [])[0].get('file')
            _temp.append({
                'type' : 'ebook',
                'filename' : filename,
                'extension' : extension,
                'download_url' : download_url
                })
        return _temp

    def _extract_audio(self, assets):
        _temp = []
        download_urls = assets.get('download_urls')
        filename = self._sanitize(assets.get('filename'))
        if download_urls and isinstance(download_urls, dict):
            extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
            download_url = download_urls.get('Audio', [])[0].get('file')
            _temp.append({
                'type' : 'audio',
                'filename' : filename,
                'extension' : extension,
                'download_url' : download_url
                })
        return _temp

    def _extract_sources(self, sources):
        _temp   =   []
        if sources and isinstance(sources, list):
            for source in sources:
                label           = source.get('label')
                download_url    = source.get('file')
                if not download_url:
                    continue
                if label.lower() == 'audio':
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
                if source.get('type') == 'application/x-mpegURL' or 'm3u8' in download_url:
                    continue
                else:
                    _type = source.get('type')
                    _temp.append({
                        'type' : 'video',
                        'height' : height,
                        'width' : width,
                        'extension' : _type.replace('video/', ''),
                        'download_url' : download_url,
                        })
        return _temp

    def _extract_subtitles(self, tracks):
        _temp   = []
        if tracks and isinstance(tracks, list):
            for track in tracks:
                if not isinstance(track, dict):
                    continue
                if track.get('_class') != 'caption':
                    continue
                download_url = track.get('url')
                if not download_url or not isinstance(download_url, encoding):
                    continue
                lang = track.get('language') or track.get('srclang') or track.get('label') or track['locale'].get('locale').split('_')[0]
                ext = 'vtt' if 'vtt' in download_url.rsplit('.', 1)[-1] else 'srt'
                _temp.append({
                    'type' : 'subtitle',
                    'language' : lang,
                    'extension' : ext,
                    'download_url' : download_url,
                    })
        return _temp

    def _extract_supplementary_assets(self, supp_assets):
        _temp   =   []
        for entry in supp_assets:
            file_id = entry.get('id')
            filename = self._sanitize(entry.get('filename'))
            download_urls = entry.get('download_urls')
            external_url = entry.get('external_url')
            slide_url = entry.get('slide_urls')
            asset_type = entry.get('asset_type').lower()
            if asset_type == 'file':
                if download_urls and isinstance(download_urls, dict):
                    extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
                    download_url = download_urls.get('File', [])[0].get('file')
                    _temp.append({
                        'type' : 'file',
                        'filename' : filename,
                        'extension' : extension,
                        'download_url' : download_url,
                        })
            elif asset_type == 'sourcecode':
                if download_urls and isinstance(download_urls, dict):
                    extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
                    download_url = download_urls.get('SourceCode', [])[0].get('file')
                    _temp.append({
                        'type' : 'source_code',
                        'filename' : filename,
                        'extension' : extension,
                        'download_url' : download_url,
                        })
            elif asset_type == 'externallink':
                _temp.append({
                    'type' : 'external_link',
                    'filename' : filename,
                    'extension' : 'txt',
                    'download_url' : external_url,
                    })
        return _temp

    def _real_extract(self, url=''):

        _udemy      =   {}
        course_id, course_info = self._extract_course_info(url)

        if course_info and isinstance(course_info, dict):
            name = course_info.get('url').replace('/', '')
            course_title = name if name else self._course_name(url)
            isenrolled = course_info['features'].get('enroll')
            if not isenrolled:
                sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Udemy Says you are not enrolled in course.")
                sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to logout now...\n")
                if not self._cookies:
                    self._logout()
                sys.stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sb + "Logged out successfully.\n")
                sys.exit(0)
        else:
            course_title = self._course_name(url)

        course_json = self._extract_course_json(course_id)
        course = course_json.get('results')
        resource = course_json.get('detail')

        if resource:
            if not self._cookies:
                sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Udemy Says : {}{}{} Run udemy-dl against course within few seconds.\n".format(resource, fw, sb))
            if self._cookies:
                sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Udemy Says : {}{}{} cookies seems to be expired.\n".format(resource, fw, sb))
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to logout now...\n")
            if not self._cookies:
                self._logout()
            sys.stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sb + "Logged out successfully.\n")
            sys.exit(0)

        _udemy['course_id'] = course_id
        _udemy['course_title'] = course_title
        _udemy['chapters'] = []
        
        counter = -1
        
        if course:
            for entry in course:

                clazz = entry.get('_class')
                asset = entry.get('asset')
                supp_assets = entry.get('supplementary_assets')
                
                if clazz == 'chapter':
                    lectures = []
                    chapter_index = entry.get('object_index')
                    chapter_title = self._clean(self._sanitize(entry.get('title')))
                    chapter = "{0:02d} {1!s}".format(chapter_index, chapter_title)
                    unsafe_chapter = u'{0:02d} '.format(chapter_index) + self._clean(entry.get('title'))
                    if chapter not in _udemy['chapters']:
                        _udemy['chapters'].append({
                            'chapter_title' : chapter,
                            'chapter_id' : entry.get("id"),
                            'chapter_index' : chapter_index,
                            'unsafe_chapter' : unsafe_chapter,
                            'lectures' : [],
                            })
                        counter += 1
                elif clazz == 'lecture':

                    lecture_id          =   entry.get("id")
                    if len(_udemy['chapters']) == 0:
                        lectures = []
                        chapter_index = entry.get('object_index')
                        chapter_title = self._clean(self._sanitize(entry.get('title')))
                        chapter = "{0:03d} {1!s}".format(chapter_index, chapter_title)
                        unsafe_chapter = u'{0:02d} '.format(chapter_index) + self._clean(entry.get('title'))
                        if chapter not in _udemy['chapters']:
                            _udemy['chapters'].append({
                                'chapter_title' : chapter,
                                'chapter_id' : lecture_id,
                                'chapter_index' : chapter_index,
                                'unsafe_chapter' : unsafe_chapter,
                                'lectures' : [],
                                })
                            counter += 1

                    if lecture_id:

                        view_html   = entry.get('view_html')
                        retVal      = []


                        if isinstance(asset, dict):
                            asset_type = asset.get('asset_type').lower() or asset.get('assetType').lower()
                            if asset_type == 'article':
                                if isinstance(supp_assets, list) and len(supp_assets) > 0:
                                    retVal  =   self._extract_supplementary_assets(supp_assets)
                            elif asset_type == 'video':
                                if isinstance(supp_assets, list) and len(supp_assets) > 0:
                                    retVal  =   self._extract_supplementary_assets(supp_assets)
                            elif asset_type == 'e-book':
                                retVal      = self._extract_ebook(asset)
                            elif asset_type == 'file':
                                retVal      = self._extract_file(asset)
                            elif asset_type == 'presentation':
                                retVal      = self._extract_ppt(asset)
                            elif asset_type == 'audio':
                                retVal      = self._extract_audio(asset)


                        if view_html:
                            text = '\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading course information .. "
                            self._spinner(text)
                            lecture_index   = entry.get('object_index')
                            lecture_title   = self._sanitize(entry.get('title'))
                            lecture         = "{0:03d} {1!s}".format(lecture_index, lecture_title)
                            unsafe_lecture  = u'{0:03d} '.format(lecture_index) + entry.get('title')
                            data, subs      = self._html_to_json(view_html, lecture_id)
                            if data and isinstance(data, dict):
                                sources     = data.get('sources')
                                tracks      = data.get('tracks') if isinstance(data.get('tracks'), list) else subs
                                duration    = data.get('duration')
                                lectures.append({
                                    'lecture_index' :   lecture_index,
                                    'lectures_id' : lecture_id,
                                    'lecture_title' : lecture,
                                    'unsafe_lecture' : unsafe_lecture,
                                    'duration' : duration,
                                    'assets' : retVal,
                                    'assets_count' : len(retVal),
                                    'sources' : self._extract_sources(sources),
                                    'subtitles' : self._extract_subtitles(tracks),
                                    'subtitle_count' : len(self._extract_subtitles(tracks)),
                                    'sources_count' : len(self._extract_sources(sources)),
                                    })
                            else:
                                lectures.append({
                                    'lecture_index' : lecture_index,
                                    'lectures_id' : lecture_id,
                                    'lecture_title' : lecture,
                                    'unsafe_lecture' : unsafe_lecture,
                                    'html_content' : view_html,
                                    'extension' : 'html',
                                    'assets' : retVal,
                                    'assets_count' : len(retVal),
                                    'subtitle_count' : 0,
                                    'sources_count' : 0,
                                    })
                        if not view_html:
                            text = '\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading course information .. "
                            self._spinner(text)
                            lecture_index   = entry.get('object_index')
                            lecture_title   = self._sanitize(entry.get('title'))
                            lecture         = "{0:03d} {1!s}".format(lecture_index, lecture_title)
                            unsafe_lecture  = u'{0:03d} '.format(lecture_index) + self._clean(entry.get('title'))
                            data            = asset.get('stream_urls')
                            if data and isinstance(data, dict):
                                sources     = data.get('Video')
                                tracks      = asset.get('captions')
                                duration    = asset.get('time_estimation')
                                lectures.append({
                                    'lecture_index' :   lecture_index,
                                    'lectures_id' : lecture_id,
                                    'lecture_title' : lecture,
                                    'unsafe_lecture' : unsafe_lecture,
                                    'duration' : duration,
                                    'assets' : retVal,
                                    'assets_count' : len(retVal),
                                    'sources' : self._extract_sources(sources),
                                    'subtitles' : self._extract_subtitles(tracks),
                                    'subtitle_count' : len(self._extract_subtitles(tracks)),
                                    'sources_count' : len(self._extract_sources(sources)),
                                    })
                            else:
                                lectures.append({
                                    'lecture_index' : lecture_index,
                                    'lectures_id' : lecture_id,
                                    'lecture_title' : lecture,
                                    'unsafe_lecture' : unsafe_lecture,
                                    'html_content' : asset.get('body'),
                                    'extension' : 'html',
                                    'assets' : retVal,
                                    'assets_count' : len(retVal),
                                    'subtitle_count' : 0,
                                    'sources_count' : 0,
                                    })

                    _udemy['chapters'][counter]['lectures'] = lectures
                    _udemy['chapters'][counter]['lectures_count'] = len(lectures)
                elif clazz == 'quiz':
                    lecture_id          =   entry.get("id")
                    if len(_udemy['chapters']) == 0:
                        lectures        =   []
                        chapter_index   =   entry.get('object_index')
                        chapter_title   =   self._clean(self._sanitize(entry.get('title')))
                        chapter         =   "{0:03d} {1!s}".format(chapter_index, chapter_title)
                        unsafe_chapter  =  u'{0:02d} '.format(chapter_index) + self._clean(entry.get('title'))
                        if chapter not in _udemy['chapters']:
                            _udemy['chapters'].append({
                                'chapter_title' : chapter,
                                'unsafe_chapter' : unsafe_chapter,
                                'chapter_id' : lecture_id,
                                'chapter_index' : chapter_index,
                                'lectures' : [],
                                })
                            counter += 1
                    _udemy['chapters'][counter]['lectures'] = lectures
                    _udemy['chapters'][counter]['lectures_count'] = len(lectures)
            _udemy['total_chapters'] = len(_udemy['chapters'])
            _udemy['total_lectures'] = sum([entry.get('lectures_count', 0) for entry in _udemy['chapters'] if entry])

        return _udemy
