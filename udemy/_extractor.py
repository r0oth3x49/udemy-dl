#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
from . import __author__
from . import __version__
from .colorized import *
from pprint import pprint
from ._compat import (
    re,
    get_url,
    requests,
    login_url,
    course_url,
    std_headers,
    login_popup,
    num_lectures,
    conn_error,
    course_list,
    compat_str,
    logout_url,
    attached_file_url,
    )
from ._utils import (
    _parse_json,
    js_to_json,
    _search_regex,
    _hidden_inputs,
    _search_simple_regex,
    unescapeHTML,
    )
early_py_version = sys.version_info[:2] < (2, 7)

class Session:

    headers = std_headers
    
    def __init__(self):
        self.session = requests.sessions.Session()

    def set_auth_headers(self, access_token, client_id):
        """Setting up authentication headers."""
        self.headers['X-Udemy-Bearer-Token']    = access_token
        self.headers['X-Udemy-Client-Id']       = client_id
        self.headers['Authorization']           = "Bearer {}".format(access_token)
        self.headers['X-Udemy-Authorization']   = "Bearer {}".format(access_token)
  
    def get(self, url):
        """Retrieving content of a given url."""
        return self.session.get(url, headers=self.headers)

    def post(self, url, data):
        """HTTP post given data with requests object."""
        return self.session.post(url, data, headers=self.headers)
    
session = Session()

class UdemyInfoExtractor:    

    def match_id(self, url):
        if '/learn/v4' in url:
            url = url.split("learn/v4")[0]
        course_name = url.split("/")[-1] if not url.endswith("/") else url.split("/")[-2]
        return course_name

    def _sanitize_title(self, title):
        # Spanish vowels characters to english vowels character
        _temp   = ''.join([str(ord(i)) if ord(i) > 128 else i for i in title])
        if '225' in _temp:
            _temp = _temp.replace('225', 'a')
        if '233' in _temp:
            _temp = _temp.replace('233', 'e')
        if '237' in _temp:
            _temp = _temp.replace('237', 'i')
        if '243' in _temp:
            _temp = _temp.replace('243', 'o')
        if '250' in _temp:
            _temp = _temp.replace('250', 'u')
        if '252' in _temp:
            _temp = _temp.replace('252', 'u')
        if '241' in _temp:
            _temp = _temp.replace('241', 'n')
        if '191' in _temp:
            _temp = _temp.replace('191', '')

        if '193' in _temp:
            _temp = _temp.replace('193', 'A')
        if '201' in _temp:
            _temp = _temp.replace('201', 'E')
        if '205' in _temp:
            _temp = _temp.replace('205', 'I')
        if '211' in _temp:
            _temp = _temp.replace('211', 'O')
        if '218' in _temp:
            _temp = _temp.replace('218', 'U')
        if '220' in _temp:
            _temp = _temp.replace('220', 'U')
        if '209' in _temp:
            _temp = _temp.replace('209', 'N')

        # fixed issue #51 - Turkish character problem 
        if '231' in _temp:
            _temp = _temp.replace('231', 'ç')
        if 'c807' in _temp:
            _temp = _temp.replace('c807', 'ç')
        if '287' in _temp:
            _temp = _temp.replace('287', 'ğ')
        if 'g774' in _temp:
            _temp = _temp.replace('g774', 'Ğ')
        if '305' in _temp:
            _temp = _temp.replace('305', 'ı')
        if '246' in _temp:
            _temp = _temp.replace('246', 'ö')
        if 'o776' in _temp:
            _temp = _temp.replace('o776', 'ö')
        if '351' in _temp:
            _temp = _temp.replace('351', 'ş')
        if 's807' in _temp:
            _temp = _temp.replace('s807', 'ş')
        if '252' in _temp:
            _temp = _temp.replace('252', 'ü')
        if 'u776' in _temp:
            _temp = _temp.replace('u776', 'ü')

        if '199' in _temp:
            _temp = _temp.replace('199', 'Ç')
        if 'C807' in _temp:
            _temp = _temp.replace('C807', 'Ç')
        if '286' in _temp:
            _temp = _temp.replace('286', 'Ğ')
        if 'G774' in _temp:
            _temp = _temp.replace('G774', 'Ğ')
        if '304' in _temp:
            _temp = _temp.replace('304', 'İ')
        if 'I775' in _temp:
            _temp = _temp.replace('I775', 'İ')
        if '214' in _temp:
            _temp = _temp.replace('214', 'Ö')
        if 'O776' in _temp:
            _temp = _temp.replace('o776', 'Ö')
        if '350' in _temp:
            _temp = _temp.replace('350', 'Ş')
        if 'S807' in _temp:
            _temp = _temp.replace('S807', 'Ş')
        if '220' in _temp:
            _temp = _temp.replace('220', 'Ü')
        if 'U776' in _temp:
            _temp = _temp.replace('U776', 'Ü')

        ok = re.compile(r'[^/]')
        if os.name == "nt":
            ok = re.compile(r'[^\\/:.*?"<>|,]')

        _title      = ''.join(x if ok.match(x) else "_" for x in _temp)
        __title     = re.sub('\d+', '', _title)

        print(__title)
        return __title

    def _get_csrf_token(self, webpage):
        try:
           match = _search_simple_regex(r"name='csrfmiddlewaretoken'\s+value='(.*)'", webpage)
           return match.group(1)
        except AttributeError:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "failed to extract csrf_token from login form try again ..\n")
            sys.exit(0)

    def _form_hidden_inputs(self, form_id, html):
        form    =   _search_regex(
                        r'(?is)<form[^>]+?id=(["\'])%s\1[^>]*>(?P<form>.+?)</form>' % form_id,
                        html,
                        '%s form' % form_id,
                        group='form'
                            )
        return _hidden_inputs(form)

    def _fill_login_form(self, login_popup, username, password):
        try:
            webpage = session.get(login_popup).text
        except conn_error as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
            time.sleep(0.8)
            sys.exit(0)
        else:
            login_form = self._form_hidden_inputs('login-form', webpage)
            login_form.update({
                'email'     : username,
                'password'  : password,
                })
        if login_form and isinstance(login_form, dict):
            return login_form
        else:
            csrf_token = self._get_csrf_token(webpage)
            login_form = {
                            'isSubmitted': 1, 
                            'email': username, 
                            'password': password,
                            'displayType': 'ajax', 
                            'csrfmiddlewaretoken': csrf_token
                        }
            return login_form

    def _extract_course_info(self, url):
        try:
            webpage    = session.get(url).text
        except conn_error as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
            time.sleep(0.8)
            sys.exit(0)
        else:
            course      = _parse_json(
                            _search_regex(
                                            r'ng-init=["\'].*\bcourse=({.+?});', 
                                            webpage, 
                                            'course', 
                                            default='{}'
                                    ),
                                    "Course Information",
                                    transform_source=unescapeHTML,
                                    fatal=False,
                                )
            course_id   = course.get('id') or _search_regex(
                                                            (r'&quot;id&quot;\s*:\s*(\d+)', r'data-course-id=["\'](\d+)'),
                                                            webpage, 
                                                            'course id'
                                                            )
        if course_id:
            return course_id
        else:
            sys.exit(0)

    def login(self, username, password):
        sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to login as " + fm + sb +"(%s)" % (username) +  fg + sb +"...\n")
        login_form      = self._fill_login_form(login_popup, username, password)
        if login_form and isinstance(login_form, dict):
            response        = session.post(login_url, data=login_form)
            access_token    = response.cookies.get('access_token')
            client_id       = response.cookies.get('client_id')
            response_text   = response.text
            if access_token and client_id:
                session.set_auth_headers(access_token, client_id)
                sys.stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sb + "Logged in successfully.\n")
            else:
                resp = response_text.split('<div class="form-errors alert alert-block alert-danger"><ul><li>')[1].split('</li></ul></div>')[0]
                sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Udemy Says: %s.\n" % (resp))
                time.sleep(0.8)
                sys.exit(0)
        else:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Failed to login ..\n")
            sys.exit(0)


    def logout(self):
        sys.stdout.write('\n')
        sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloaded course information webpages successfully..\n")
        sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to logout now...\n")
        try:
            session.get(logout_url)
        except conn_error as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
            time.sleep(0.8)
            sys.exit(0)
        else:
            sys.stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sb + "Logged out successfully.\n")

    def _lecture_count(self, response):
        count = 0
        for entry in response['results']:
            clazz = entry.get('_class')
            if clazz == 'lecture':
                asset = entry.get('asset')
                if isinstance(asset, dict):
                    asset_type = asset.get('asset_type') or asset.get('assetType')
                    if asset_type == 'Video':
                        count += 1
                    elif asset_type == 'E-Book':
                        count += 1
                    elif asset_type == 'File':
                        count += 1
                    elif asset_type == 'Presentation':
                        count += 1
                    elif asset_type == 'Article':
                        count += 1
                    else:
                        count = count
        return count

    def _generate_dirname(self, title):
        ok = re.compile(r'[^/]')

        if os.name == "nt":
            ok = re.compile(r'[^\\/:.*?"<>|,]')

        dirname = "".join(x if ok.match(x) else "_" for x in title)
        return dirname

    def Progress(self, iteration, total, prefix = '' , fileSize='' , downloaded = '' , barLength = 100):
        filledLength    = int(round(barLength * iteration / float(total)))
        percents        = format(100.00 * (iteration / float(total)), '.2f')
        bar             = fm + sd + '=' * filledLength + fg + sd + '-' * (barLength - filledLength)
        sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + 'Extracting ' + fg + sb + '(' + str(fileSize) + '/' + str(downloaded) + ') |' + bar + fg + sb + '| ' + percents + '%                                      \r')
        sys.stdout.flush()
        

    def real_extract(self, url, course_name, course_path):

        rootDir = course_name
        
        course_id = self._extract_course_info(url)
        _course_url = course_url.format(course_id=course_id)
        response = session.get(_course_url).json()
        _isenrolled = response.get('detail')
        if _isenrolled:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "You are not enrolled in this course Udemy Says : {}.".format(_isenrolled))
            self.logout()
            exit(0)
        num_lect =  int(self._lecture_count(response))
        sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Found (%s) lectures ...\n" % (num_lect))
        
        udemy_dict = {}
        chap, chapter_number = [None] * 2
        counter = 0
        
        for entry in response['results']:
            clazz = entry.get('_class')
            if clazz == 'lecture':
                if len(udemy_dict) == 0:
                    ind     = entry.get('object_index')
                    _title  = self._sanitize_title(entry.get('title'))
                    t       = (''.join([i if ord(i) < 128 else ' ' for i in _title]))
                    chap    = "{0:03d} {1!s}".format(ind, t if '.' not in t else t.replace('.', '_'))
                    if chap not in udemy_dict:
                        udemy_dict[chap] = {}
                
                asset                = entry.get('asset')
                lecture_id           = entry.get("id")
                supplementary_assets = entry.get('supplementary_assets')

                if isinstance(asset, dict):
                    asset_type = asset.get('asset_type') or asset.get('assetType')
                    if asset_type == 'Article':
                        if len(supplementary_assets) != 0:
                            
                            if isinstance(supplementary_assets, list):
                                for _asset in supplementary_assets:
                                    _file_id        = _asset.get('id')
                                    _filename       = _asset.get('filename')
                                    _download_urls  = _asset.get('download_urls')
                                    _external_url   = _asset.get('external_url')
                                    _slide_url      = _asset.get('slide_urls')
                                    _asset_type     = _asset.get('asset_type')

                                if _asset_type == 'ExternalLink':
                                    if lecture_id not in udemy_dict[chap]:
                                        src         = {'external_url'   :   _external_url}
                                        title       = _filename
                                        udemy_dict[chap][title] = {}
                                        if _filename not in udemy_dict[chap][title]:
                                            udemy_dict[chap][title] = src
                                            
                                elif _asset_type == 'File':
                                    if isinstance(_download_urls, dict):
                                        src     =   _download_urls.get('File')[0]
                                    if lecture_id not in udemy_dict[chap]:
                                        ind         = entry.get('object_index')
                                        title       = "{0:03d} {1!s}".format(ind, _filename)
                                        udemy_dict[chap][title] = {}
                                        if _filename not in udemy_dict[chap][title]:
                                            udemy_dict[chap][title] = src

                                elif _asset_type == 'SourceCode':
                                    if isinstance(_download_urls, dict):
                                        src     =   _download_urls.get('SourceCode')[0]
                                    if lecture_id not in udemy_dict[chap]:
                                        ind         = entry.get('object_index')
                                        title       = "{0:03d} {1!s}".format(ind, _filename)
                                        udemy_dict[chap][title] = {}
                                        if _filename not in udemy_dict[chap][title]:
                                            udemy_dict[chap][title] = src
                            counter += 1
                            
                        else:
                            counter += 1
                        
                    elif asset_type == 'Video':
                        
                        if len(supplementary_assets) != 0:
                            
                            if isinstance(supplementary_assets, list):
                                for _asset in supplementary_assets:
                                    _file_id        = _asset.get('id')
                                    _filename       = _asset.get('filename')
                                    _download_urls  = _asset.get('download_urls')
                                    _external_url   = _asset.get('external_url')
                                    _slide_url      = _asset.get('slide_urls')
                                    _asset_type     = _asset.get('asset_type')


                            if _asset_type == 'ExternalLink':
                                if lecture_id not in udemy_dict[chap]:
                                    src         = {'external_url'   :   _external_url}
                                    title       = _filename
                                    udemy_dict[chap][title] = {}
                                    if _filename not in udemy_dict[chap][title]:
                                        udemy_dict[chap][title] = src

                            elif _asset_type == 'File':
                                if isinstance(_download_urls, dict):
                                    src     =   _download_urls.get('File')[0]
                                if lecture_id not in udemy_dict[chap]:
                                    ind         = entry.get('object_index')
                                    title       = "{0:03d} {1!s}".format(ind, _filename)
                                    udemy_dict[chap][title] = {}
                                    if _filename not in udemy_dict[chap][title]:
                                        udemy_dict[chap][title] = src

                            elif _asset_type == 'SourceCode':
                                if isinstance(_download_urls, dict):
                                    src     =   _download_urls.get('SourceCode')[0]
                                if lecture_id not in udemy_dict[chap]:
                                    ind         = entry.get('object_index')
                                    title       = "{0:03d} {1!s}".format(ind, _filename)
                                    udemy_dict[chap][title] = {}
                                    if _filename not in udemy_dict[chap][title]:
                                        udemy_dict[chap][title] = src
                                    
                            counter += 1
                        else:
                            counter += 1
                        
                    elif asset_type == 'E-Book':
                        _items      = asset.get('download_urls')
                        _filename   = asset.get('filename')
                        if isinstance(_items, dict):
                            src       = _items.get('E-Book')[0]

                        if lecture_id not in udemy_dict[chap]:
                            ind         = entry.get('object_index')
                            title       = "{0:03d} {1!s}".format(ind, _filename)
                            udemy_dict[chap][title] = {}
                            
                            if _filename not in udemy_dict[chap][title]:
                                udemy_dict[chap][title] = src
                                
                        counter += 1
                        
                    elif asset_type == 'File':
                        
                        _items      = asset.get('download_urls')
                        _filename   = asset.get('filename')
                        if isinstance(_items, dict):
                            src       = _items.get('File')[0]

                        if lecture_id not in udemy_dict[chap]:
                            ind         = entry.get('object_index')
                            title       = "{0:03d} {1!s}".format(ind, _filename)
                            udemy_dict[chap][title] = {}
                            
                            if _filename not in udemy_dict[chap][title]:
                                udemy_dict[chap][title] = src
                                
                        counter += 1

                        
                    elif asset_type == 'Presentation':
                        
                        __items     = asset.get('download_urls')
                        _items      = asset.get('slide_urls')
                        _filename   = asset.get('filename')
                        if __items and isinstance(__items, dict):
                            src     = __items.get('Presentation')[0]
                        elif _items and isinstance(_items, list):
                            ext_list = ['.png', '.jpg', '.jpeg']
                            src     = {'file' : compat_str(_items[0]), 'label' : 'download'}
                            matching = [ext for ext in ext_list if ext in src.get('file')]
                            if matching:
                                _filename = '{}{}'.format(_filename.split('.')[0],matching[0])

                        if lecture_id not in udemy_dict[chap]:
                            ind         = entry.get('object_index')
                            title       = "{0:03d} {1!s}".format(ind, _filename)
                            udemy_dict[chap][title] = {}
                            
                            if _filename not in udemy_dict[chap][title]:
                                udemy_dict[chap][title] = src
                                
                        counter += 1
                        
                    else:
                        counter = counter
                        
                self.Progress(counter, num_lect, fileSize = str(num_lect), downloaded = str(counter), barLength = 40)
                time.sleep(0.1)
                if lecture_id:
                    try:
                        if lecture_id not in udemy_dict[chap]:
                            view_html = entry.get('view_html')
                            if view_html:
                                ind = entry.get('object_index')
                                _title  = self._sanitize_title(entry.get('title'))
                                t = (''.join([i if ord(i) < 128 else ' ' for i in _title]))
                                title = "{0:03d} {1!s}".format(ind, t if '.' not in t else t.replace('.', '_'))
                                udemy_dict[chap][title] = {}
                                data   = _parse_json(
                                                    _search_regex(
                                                            r'videojs-setup-data=(["\'])(?P<data>{.+?})\1',
                                                            view_html,
                                                            'setup data',
                                                            default='{}',
                                                            group='data'),
                                                    lecture_id,
                                                    transform_source=unescapeHTML,
                                                    fatal=False,
                                    )
                                text_tracks = _parse_json(
                                                    _search_regex(
                                                            r'text-tracks=(["\'])(?P<data>\[.+?\])\1',
                                                            view_html,
                                                            'text tracks',
                                                            default='{}',
                                                            group='data'),
                                                    lecture_id,
                                                    transform_source=lambda s: js_to_json(unescapeHTML(s)),
                                                    fatal=False,
                                    )
                                if data and isinstance(data, dict):
                                    sources  = data.get('sources')
                                    tracks   = data.get('tracks') if isinstance(data.get('tracks'), list) else text_tracks
                                    duration = data.get('durations') if not None else None
                                    if isinstance(sources, list):
                                        for source in sources:
                                            res  = source.get('label')
                                            src  = source.get('src')
                                            if not src:
                                                continue
                                            height = res if res else None
                                            if source.get('type') == 'application/x-mpegURL' or 'm3u8' in src:
                                                continue
                                            else:
                                                udemy_dict[chap][title][src] = height

                                                
                                    if isinstance(tracks, list):
                                        for track in tracks:
                                            if not isinstance(track, dict):
                                                continue
                                            if track.get('kind') != 'captions':
                                                continue
                                            src = track.get('src')
                                            if not src or not isinstance(src, compat_str):
                                                continue
                                            lang = track.get('language') or track.get('srclang') or track.get('label')
                                            autogenerated = track.get('autogenerated')
                                            ext      = 'vtt' if 'vtt' in src.rsplit('.', 1)[-1] else 'srt'
                                            subtitle = "{}-subtitle-{}.{}".format(title,lang, ext)
                                            if not subtitle in udemy_dict[chap]:
                                                udemy_dict[chap][subtitle] = {'subtitle' : src}
                                else:
                                    udemy_dict[chap][title]["view_html"] = view_html
                                    
                        if chapter_number:
                            entry['chapter_number'] = chapter_number
                        if chapter:
                            entry['chapter'] = chapter
                    except Exception as e:
                        pass

                        
            elif clazz == 'chapter':
                chapter_number = entry.get('object_index')
                _title  = self._sanitize_title(entry.get('title'))              
                title = _title
                chapter = self._generate_dirname(title)
                chap = "{0:02d} {1!s}".format(chapter_number, chapter)
                if chap not in udemy_dict:
                    udemy_dict[chap] = {}

        return udemy_dict
