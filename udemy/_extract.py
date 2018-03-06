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
            time,
            encoding,
            conn_error,
            COURSE_URL,
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

    def _course_name(self, url):
        if '/learn/v4' in url:
            url = url.split("learn/v4")[0]
        course_name = url.split("/")[-1] if not url.endswith("/") else url.split("/")[-2]
        return course_name
    
    def _sanitize(self, unsafetext):
        text = sanitize(slugify(unsafetext, lower=False, spaces=True, ok=SLUG_OK + '().'))
        return text

    def _login(self, username='', password=''):
        auth = UdemyAuth(username=username, password=password)
        self._session = auth.authenticate()
        if self._session is not None:
            return {'login' : 'successful'}
        else:
            return {'login' : 'failed'}
    
    def _logout(self):
        return self._session.terminate()

    def _extract_course_info(self, url):
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
                                                (r'&quot;id&quot;\s*:\s*(\d+)', r'data-course-id=["\'](\d+)'),
                                                webpage, 
                                                'course id'
                                                )
        if course_id:
            return course_id, course
        else:
            sys.exit(0)

    def _extract_course_json(self, course_id):
        url = COURSE_URL.format(course_id=course_id)
        try:
            resp = self._session._get(url).json()
        except conn_error as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
            time.sleep(0.8)
            sys.exit(0)
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

    def _extract_sources(self, sources):
        _temp   =   []
        if sources and isinstance(sources, list):
            for source in sources:
                label           = source.get('label')
                download_url    = source.get('src')
                if not download_url:
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
                if track.get('kind') != 'captions':
                    continue
                download_url = track.get('src')
                if not download_url or not isinstance(download_url, encoding):
                    continue
                lang = track.get('language') or track.get('srclang') or track.get('label')
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

    def _lectures_count(self, chapters):
        lectures = 0
        for entry in chapters:
            lectures_count = entry.get('lectures_count')
            lectures += lectures_count
        return lectures

    def _real_extract(self, url=''):

        _udemy      =   {}
        course_id, course_info = self._extract_course_info(url)

        if course_info and isinstance(course_info, dict):
            course_title = self._course_name(url)
            isenrolled = course_info['features'].get('enroll')
            if not isenrolled:
                sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Udemy Says you are not enrolled in course.")
                sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to logout now...\n")
                self._logout()
                sys.stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sb + "Logged out successfully.\n")
                sys.exit(0)
        else:
            course_title = self._course_name(url)

        course_json = self._extract_course_json(course_id)
        course = course_json.get('results')
        resource = course_json.get('detail')

        if resource:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Udemy Says : {}{}{} Run udemy-dl against course within few seconds.\n".format(resource, fw, sb))
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to logout now...\n")
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
                    chapter_title = self._sanitize(entry.get('title'))
                    chapter_title = re.sub('\.+$', '', chapter_title) if chapter_title.endswith(".") else chapter_title
                    chapter = "{0:02d} {1!s}".format(chapter_index, chapter_title)
                    if chapter not in _udemy['chapters']:
                        _udemy['chapters'].append({
                            'chapter_title' : chapter,
                            'chapter_id' : entry.get("id"),
                            'chapter_index' : chapter_index,
                            'lectures' : [],
                            })
                        counter += 1
                elif clazz == 'lecture':

                    lecture_id          =   entry.get("id")
                    if len(_udemy['chapters']) == 0:
                        lectures        =   []
                        chapter_index   =   entry.get('object_index')
                        chapter_title   =   self._sanitize(entry.get('title'))
                        chapter_title   =   re.sub('\.+$', '', chapter_title) if chapter_title.endswith(".") else chapter_title
                        chapter         =   "{0:03d} {1!s}".format(chapter_index, chapter_title)
                        if chapter not in _udemy['chapters']:
                            _udemy['chapters'].append({
                                'chapter_title' : chapter,
                                'chapter_id' : lecture_id,
                                'chapter_index' : chapter_index,
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


                        if view_html:
                            text = '\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading course information .. "
                            self._spinner(text)
                            lecture_index   = entry.get('object_index')
                            lecture_title   = self._sanitize(entry.get('title'))
                            lecture         = "{0:03d} {1!s}".format(lecture_index, lecture_title)
                            data, subs      = self._html_to_json(view_html, lecture_id)
                            if data and isinstance(data, dict):
                                sources     = data.get('sources')
                                tracks      = data.get('tracks') if isinstance(data.get('tracks'), list) else subs
                                duration    = data.get('duration')
                                lectures.append({
                                    'lecture_index' :   lecture_index,
                                    'lectures_id' : lecture_id,
                                    'lecture_title' : lecture,
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
                                    'html_content' : view_html,
                                    'extension' : 'html',
                                    'assets' : retVal,
                                    'assets_count' : len(retVal),
                                    'subtitle_count' : 0,
                                    'sources_count' : 0,      
                                    })

                    _udemy['chapters'][counter]['lectures'] = lectures
                    _udemy['chapters'][counter]['lectures_count'] = len(lectures)
            _udemy['total_chapters'] = len(_udemy['chapters'])
            _udemy['total_lectures'] = self._lectures_count(_udemy['chapters'])

        return _udemy
