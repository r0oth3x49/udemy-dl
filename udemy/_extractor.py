#!/usr/bin/python

import os,sys,time
from colorized import *
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
    )
from _utils import (
                    extract_attributes,
                    extract_videojs_data,
                    unescapeHTML,
                    _search_regex,
                    _convert_to_dict,
                    )
early_py_version = sys.version_info[:2] < (2, 7)

class Session:

    headers = std_headers
    
    def __init__(self):
        self.session = requests.sessions.Session()

    def set_auth_headers(self, access_token, client_id):
        """Setting up authentication headers."""
        self.headers['X-Udemy-Bearer-Token'] = access_token
        self.headers['X-Udemy-Client-Id'] = client_id
        self.headers['Authorization'] = "Bearer " + access_token
        self.headers['X-Udemy-Authorization'] = "Bearer " + access_token
  
    def get(self, url):
        """Retrieving content of a given url."""
        return self.session.get(url, headers=self.headers)

    def post(self, url, data):
        """HTTP post given data with requests object."""
        return self.session.post(url, data, headers=self.headers)
    
session = Session()

class UdemyInfoExtractor:    

    def match_id(self, url):
        course_name = url.split("/")[-1] if not url.endswith("/") else url.split("/")[-2]
        return course_name
    
    def _get_csrf_token(self):
        try:
           response = session.get(login_popup)
           match = re.search(r"name='csrfmiddlewaretoken'\s+value='(.*)'", response.text)
           return match.group(1)
        except AttributeError:
            session.get(logout)
            response = re.search(r"name='csrfmiddlewaretoken'\s+value='(.*)'", response.text)
            return match.group(1)

    def _get_course_id(self, url):

        response = session.get(url)
        response_text = response.text

        matches = re.search(r'data-course-id="(\d+)"', response_text, re.IGNORECASE)
        if matches:
            course_id = matches.groups()[0]
        else:
            matches = re.search(r'property="og:image"\s+content="([^"]+)"', response_text, re.IGNORECASE)
            course_id = matches.groups()[0].rsplit('/', 1)[-1].split('_', 1)[0] if matches else None
        if not course_id:
            sys.exit(1)
        else:
            return course_id

    def _regex_course_id(self, url):
        response = session.get(url)
        webpage = response.text
        course_id = unescapeHTML(_search_regex(r'(?<=&quot;id&quot;:\s)(\d+)',webpage).group())
        if course_id:
            return course_id
        else:
            sys.exit(0)

    def login(self, username, password):
        csrf_token = self._get_csrf_token()
        session.get('http://www.udemy.com/user/logout')
        sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to login as " + fm + sb +"(%s)" % (username) +  fg + sb +"...\n")
        payload = {'isSubmitted': 1, 'email': username, 'password': password,
               'displayType': 'ajax', 'csrfmiddlewaretoken': csrf_token}
        response = session.post(login_url, payload)

        access_token = response.cookies.get('access_token')
        client_id = response.cookies.get('client_id')
        response_text = response.text
        if access_token and client_id:
            session.set_auth_headers(access_token, client_id)
            sys.stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sb + "Logged in successfully.\n")
        else:
            resp = response_text.split('<div class="form-errors alert alert-block alert-danger"><ul><li>')[1].split('</li></ul></div>')[0]
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Udemy Says: %s.\n" % (resp))
            time.sleep(0.8)
            sys.exit(0)


    def logout(self):
        sys.stdout.write('\n')
        sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloaded course information webpages successfully..\n")
        sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to logout now...\n")
        session.get('http://www.udemy.com/user/logout')
        sys.stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sb + "Logged out successfully.\n")

    def _extract_course_info(self, response):
        count = 0
        for entry in response['results']:
            clazz = entry.get('_class')
            if clazz == 'lecture':
                html = entry.get('view_html')
                asset = entry.get('asset')
                if isinstance(asset, dict):
                    asset_type = asset.get('asset_type') or asset.get('assetType')
                    if asset_type == 'Video':
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
        
        course_id = self._regex_course_id(url)
        if not course_id:
            course_id = self._get_course_id(url)
        curl = course_url % (course_id)
        response = session.get(curl).json()
        num_lect = int(self._extract_course_info(response))
        sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Found (%s) video lectures ...\n" % (num_lect))
        
        udemy_dict = {}
        chapter, chapter_number = [None] * 2
        counter = 1
        
        for entry in response['results']:
            clazz = entry.get('_class')
            if clazz == 'lecture':
                asset = entry.get('asset')
                if isinstance(asset, dict):
                    asset_type = asset.get('asset_type') or asset.get('assetType')
                    if asset_type != 'Video':
                        continue
                    else:
                        self.Progress(counter, num_lect, fileSize = str(num_lect), downloaded = str(counter), barLength = 40)
                        time.sleep(0.1)
                        counter += 1
                lecture_id = entry.get("id")
                if lecture_id:
                    if lecture_id not in udemy_dict[chap]:
                        ind = entry.get('object_index')
                        t = (''.join([i if ord(i) < 128 else ' ' for i in entry.get('title')]))
                        title = "{0:03d} {1!s}".format(ind, t)
                        udemy_dict[chap][title] = []
                        asset = entry['asset']
                        video_id = asset['id']
                        

                        outputs = asset.get('data', {}).get('outputs')
                        if not isinstance(outputs, dict):
                            outputs = {}


                        def add_output_format_meta(f, key):
                            output = outputs.get(key)
                            if isinstance(output, dict):
                                output_format = extract_output_format(output)
                                output_format.update(f)
                                return output_format
                            return f

                        view_html = entry.get('view_html')
                        if view_html:
                            webpage = (view_html.split('videojs-setup-data="')[1].split('"')[0]).replace('\n', '') if '\n' else view_html.split('videojs-setup-data="')[1].split('"')[0]
                            view_html_urls = set()
                            urls_dict   = _convert_to_dict(
                                            unescapeHTML(
                                                _search_regex(
                                                        r'(?<=&quot;sources&quot;:)\s*\[(.+?)\]',
                                                        webpage).group(0)
                                                        ))
                            if isinstance(urls_dict, tuple):
                                for source in urls_dict:
                                    res = source.get('label')
                                    src = source.get('src').replace('\u0026','&')
                                    if not src:
                                        continue
                                    height = res if res else None
                                    if source.get('type') == 'application/x-mpegURL' or 'm3u8' in src:
                                        continue
                                    else:
                                        udemy_dict[chap][title].append(add_output_format_meta({
                                            height: src,}, res))
                                    
                            if isinstance(urls_dict, dict):
                                src = source.get('src').replace('\u0026','&')
                                res = source.get('label')
                                if not src:
                                    continue
                                height = res if res else None
                                if source.get('type') == 'application/x-mpegURL' or 'm3u8' in src:
                                    continue
                                else:
                                    udemy_dict[chap][title].append(add_output_format_meta({
                                        height: src,}, res))
                                
                    if chapter_number:
                        entry['chapter_number'] = chapter_number
                    if chapter:
                        entry['chapter'] = chapter
            elif clazz == 'chapter':
                chapter_number = entry.get('object_index')
                title = ''.join([i if ord(i) < 128 else ' ' for i in entry.get('title')])
                chapter = self._generate_dirname(title)
                chap = "{0:02d} {1!s}".format(chapter_number, chapter)
                if chapter_number not in udemy_dict:
                    udemy_dict[chap] = {}
                    
        return udemy_dict
