#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import time
import udemy
import optparse

from sys import *
from requests import get
from pprint import pprint
from udemy.colorized import *
from udemy import __author__
from udemy import __version__

from udemy.colorized.banner import banner

extract_info        = udemy.UdemyInfoExtractor()
course_dl           = udemy.Downloader()
getpass             = udemy.GetPass()
vtt2srt             = udemy.WEBVTT2SRT()
cache_creds         = udemy.cache_credentials
use_cached_creds    = udemy.use_cached_credentials

class UdemyDownload:

    def __init__(self, url, username, password, list_down=False, save_links=False, outto=None, quality=None):
        self.url        = url
        self.username   = username
        self.password   = password
        self.list       = list_down
        self.save       = save_links
        self.outto      = outto
        self.quality    = quality
        


    def login(self):
        extract_info.login(self.username, self.password)

    def logout(self):
        extract_info.logout()

    def Progress(self, iteration, total, prefix = '' , fileSize='' , downloaded = '' , rate = '' ,suffix = '', barLength = 100):
        filledLength    = int(round(barLength * iteration / float(total)))
        percents        = format(100.00 * (iteration / float(total)), '.2f')
        bar             = fc + sd + ('█' if os.name == 'posix' else '#') * filledLength + fg + sd +'-' * (barLength - filledLength)
        stdout.write('{}{}[{}{}*{}{}] : {}{}{}/{} {}% |{}{}{}| {} {}s ETA                                \r'.format(fc,sd,fm,sb,fc,sd,fg,sb,fileSize,downloaded,percents,bar,fg,sb,rate,suffix))
        stdout.flush()

    def clean_dict(self, udemy_dict):
        if not isinstance(udemy_dict, (dict, list)):
            return udemy_dict
        if isinstance(udemy_dict, list):
            return [v for v in (self.clean_dict(v) for v in udemy_dict) if v]
        return {k: v for k, v in ((k, self.clean_dict(v)) for k, v in udemy_dict.items()) if v}

    def Download(self, total, recvd, ratio, rate, eta):
        if total <= 1048576:
            TotalSize = round(float(total) / 1024, 2)
            Receiving = round(float(recvd) / 1024, 2)
            Size = format(TotalSize if TotalSize < 1024.00 else TotalSize/1024.00, '.2f')
            Received = format(Receiving if Receiving < 1024.00 else Receiving/1024.00,'.2f')
            SGb_SMb = 'KB' if TotalSize < 1024.00 else 'MB'
            RGb_RMb = 'KB ' if Receiving < 1024.00 else 'MB '
        else:
            TotalSize = round(float(total) / 1048576, 2)
            Receiving = round(float(recvd) / 1048576, 2)
            Size = format(TotalSize if TotalSize < 1024.00 else TotalSize/1024.00, '.2f')
            Received = format(Receiving if Receiving < 1024.00 else Receiving/1024.00,'.2f')
            SGb_SMb = 'MB' if TotalSize < 1024.00 else 'GB'
            RGb_RMb = 'MB ' if Receiving < 1024.00 else 'GB '

        Dl_Speed = round(float(rate) , 2)
        dls = format(Dl_Speed if Dl_Speed < 1024.00 else Dl_Speed/1024.00, '.2f')
        Mb_kB = 'kB/s ' if Dl_Speed < 1024.00 else 'MB/s '
        (mins, secs) = divmod(eta, 60)
        (hours, mins) = divmod(mins, 60)
        if hours > 99:
            eta = "--:--:--"
        if hours == 0:
            eta = "%02d:%02d" % (mins, secs)
        else:
            eta = "%02d:%02d:%02d" % (hours, mins, secs)
        self.Progress(Receiving, TotalSize, fileSize = str(Size) + str(SGb_SMb) , downloaded = str(Received) + str(RGb_RMb), rate = str(dls) + str(Mb_kB), suffix = str(eta), barLength = 40)

    def Downloader(self, url, title, path):
        out = course_dl.download(url, title, filepath=path, quiet=True, callback=self.Download)
        if isinstance(out, dict) and len(out) > 0:
            msg     = out.get('msg')
            status  = out.get('status')
            if status == 'True':
                return msg
            else:
                if msg == 'Udemy Says (HTTP Error 401 : Unauthorized)':
                    print (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Udemy Says (HTTP Error 401 : Unauthorized)")
                    print (fc + sd + "[" + fw + sb + "*" + fc + sd + "] : " + fw + sd + "Try to run the udemy-dl again...")
                    exit(0)
                else:
                    return msg
            
    def SaveLinks(self, quality=None, path=None, default=False):
        if not path:
            current_dir = os.getcwd()
        else:
            if os.path.exists(path):
                current_dir = path
                os.chdir(current_dir)
            else:
                current_dir = os.getcwd()
                print (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Path '%s' does not exist, saving to '%s'" % (path, current_dir))
                
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading webpage..")
        time.sleep(2)
        course_path = extract_info.match_id(self.url)
        course      = "%s" % (course_path) 
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Extracting course information..")
        time.sleep(2)
        course_name = current_dir + '\\' + course_path if os.name is 'nt' else current_dir + '/' + course_path
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading " + fb + sb + "'%s'." % (course.replace('-',' ')))
        self.login()
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading course information webpages ..")
        videos_dict = self.clean_dict(extract_info.real_extract(self.url, course_name, course_path))
        self.logout()
        if isinstance(videos_dict, dict):
            if os.name == 'nt':
                print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Saving links under '%s\\%s.txt'" % (current_dir, course))
            else:
                print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Saving links under '%s/%s.txt'" % (current_dir, course))
            for chap in sorted(videos_dict):
                for lecture_name,urls in sorted(videos_dict[chap].items()):
                    try:
                        _file           = urls.get('file')
                        _external_url   = urls.get('external_url')
                        _subtitle       = urls.get('subtitle')
                    except AttributeError as e:
                        pass
                    else:
                        if _external_url and not _file and not _subtitle:
                            _url = _external_url
                        elif _file and not _external_url and not _subtitle:
                            _url = _file
                        elif _subtitle and not _file and not _external_url:
                            _url = _subtitle
                        elif not _external_url and not _file:
                            if not quality:
                                _url = max(urls, key=urls.get)
                            else:
                                found = False
                                for url,res in urls.items():
                                    if res == quality:
                                        _url = url
                                        found = True
                                    else:
                                        continue
                                    
                                if not found:
                                    if default:
                                        print (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Request quality not found for (%s)" % (lecture_name))
                                        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fw + sb + "Downloading default quality...")
                                        try:
                                            _url = max(urls, key=urls.get)
                                        except ValueError as e:
                                            continue
                                    else:
                                        print (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Requested quality is not available for (%s)" % (lecture_name))
                                        if version_info[:2] >= (3, 0):
                                            askUser = input(fc + sd + "[" + fw + sb + "?" + fc + sd + "] : " + fw + sb + "Would you like to download the default quality (y/n): ")
                                        else:
                                            askUser = raw_input(fc + sd + "[" + fw + sb + "?" + fc + sd + "] : " + fw + sb + "Would you like to download the default quality (y/n): ")
                                        if askUser == 'y' or askUser == 'Y' or askUser == '':
                                            try:
                                                _url = max(urls, key=urls.get)
                                            except ValueError as e:
                                                continue
                                        else:
                                            print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Continuing to check for the next lecture..")
                                            continue
                        
                    if _url:
                        with open("%s.txt" % (course), "a") as f:
                            f.write("- {}\n- {}\n".format(lecture_name.encode("utf-8").strip(), _url.encode("utf-8").strip()))
                        f.close()
            print (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Saved successfully.")
                            
    def get_filsize(self, url):
        req             = get(url, stream=True)
        content_length  = float(req.headers.get('Content-Length'))
        if content_length <= 1048576.00:
            size = round(content_length / 1024, 2)
            sz = size
            in_MB = "KB "
        else:
            size = round(content_length / 1048576, 2)
            sz = size if size < 1024.00 else round(size/1024.00,2)
            in_MB = "MB " if size < 1024.00 else 'GB '

        return sz,in_MB
            
    def ListDown(self):
        current_dir = os.getcwd()
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading webpage..")
        time.sleep(2)
        course_path = extract_info.match_id(self.url)
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Extracting course information..")
        time.sleep(2)
        course_name = current_dir + '\\' + course_path if os.name is 'nt' else current_dir + '/' + course_path
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading " + fb + sb + "'%s'." % (course_path.replace('-',' ')))
        self.login()
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading course information webpages ..")
        videos_dict = self.clean_dict(extract_info.real_extract(self.url, course_name, course_path))
        self.logout()
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Extracting chapters & lectures information..")
        if isinstance(videos_dict, dict):
            for chap in sorted(videos_dict):
                print (fc + sd + "\n[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s)" % (chap))
                for lecture,urls in sorted(videos_dict[chap].items()):
                    try:
                        _file           = urls.get('file')
                        _external_url   = urls.get('external_url')
                        _subtitle       = urls.get('subtitle')
                        _view_html      = urls.get('view_html')
                    except AttributeError as e:
                        pass
                    else:
                        if _view_html:
                            pass
                        else:
                            if _external_url and not _file and not _subtitle:
                                _external_url = urls.get('external_url')
                                print  (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fy + sb + "External Link '" + fm + sd + str(lecture)+ fy + sb + "'..")
                                print  (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fy + sb + "Visit " + fg + sd + "(" + str(_external_url)+ fg + sb + ")\n")
                            elif _file and not _external_url and not _subtitle:
                                print  (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fy + sb + "File '" + fm + sd + str(lecture)+ fy + sb + "'..")
                                print  (fy + sb + "+--------------------------------------------+")
                                print  (fy + sb + "|     {:<6} {:<8} {:<7} {:<15}|".format("Stream", "Type", "Format", "Size"))
                                print  (fy + sb + "|     {:<6} {:<8} {:<7} {:<15}|".format("------", "-----", "------","-------"))
                                sid         = 1
                                url         = _file
                                sz,in_MB    = self.get_filsize(url)
                                media       = 'file' 
                                Format      = lecture.split('.')[-1]
                                print  (fy + sb + "|" + fg + sd + "     {:<6} {:<8} {:<7} {:<5} {:<8}{}{}|".format(sid, media, Format , sz, in_MB, fy, sb))
                                print  (fy + sb + "+--------------------------------------------+")
                            elif _subtitle and not _file and not _external_url:
                                print  (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fy + sb + "Subtitle '" + fm + sd + str(lecture)+ fy + sb + "'..")
                                print  (fy + sb + "+--------------------------------------------+")
                                print  (fy + sb + "|     {:<6} {:<8} {:<7} {:<15}|".format("Stream", "Type", "Format", "Size"))
                                print  (fy + sb + "|     {:<6} {:<8} {:<7} {:<15}|".format("------", "-----", "------","-------"))
                                sid         = 1
                                url         = _subtitle
                                sz,in_MB    = self.get_filsize(url)
                                media       = 'file' 
                                Format      = lecture.split('.')[-1]
                                print  (fy + sb + "|" + fg + sd + "     {:<6} {:<8} {:<7} {:<5} {:<9}{}{}|".format(sid, media, Format , sz, in_MB, fy, sb))
                                print  (fy + sb + "+--------------------------------------------+")
                            elif not _external_url and not _file and not _subtitle:
                                print  (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fy + sb + "Lecture '" + fm + sd + str(lecture)+ fy + sb + "'..")
                                print  (fy + sb + "+--------------------------------------------------------+")
                                print  (fy + sb + "|     {:<6} {:<8} {:<7} {:<12} {:<14}|".format("Stream", "Type", "Format", "Quality", "Size"))
                                print  (fy + sb + "|     {:<6} {:<8} {:<7} {:<10} {:<16}|".format("------", "-----", "------", "-------", "--------"))
                                i = 0
                                for _url,res in urls.items():
                                    sid         = i + 1
                                    quality     = res
                                    url         = _url
                                    sz,in_MB    = self.get_filsize(url)
                                    media       = 'video' 
                                    Format      = 'mp4'
                                    print  (fy + sb + "|" + fg + sd + "     {:<6} {:<8} {:<7} {:<10} {:<7}{:<9}{}{}|".format(sid, media, Format , str(quality) + 'p', sz, in_MB, fy, sb))
                                    i += 1
                                print  (fy + sb + "+--------------------------------------------------------+")

    def ExtractAndDownload(self, path=None, quality=None,  default=False, caption_only=False, skip_captions=False):
        current_dir = os.getcwd()
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading webpage..")
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Extracting course information..")
        time.sleep(2)
        course = extract_info.match_id(self.url)
        if not path:
            course_path = extract_info.match_id(self.url)
            course_name = current_dir + '\\' + course_path if os.name == 'nt' else current_dir + '/' + course_path
        else:
            if '~' in path:
                path    = os.path.expanduser(path)
            course_path = "%s\\%s" % (path, extract_info.match_id(self.url)) if os.name == 'nt' else "%s/%s" % (path, extract_info.match_id(self.url))
            course_name = course_path
            
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading " + fb + sb + "'%s'." % (course.replace('-',' ')))
        self.login()
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading course information webpages ..")
        videos_dict = self.clean_dict(extract_info.real_extract(self.url, course_name, course_path))
        self.logout()
        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Counting no of chapters..")
        if isinstance(videos_dict, dict):
            print (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fw + sd + "Found ('%s') chapter(s).\n" % (len(videos_dict)))
            j = 1
            for chap in sorted(videos_dict):
                print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fm + sb + "Downloading chapter : (%s of %s)" % (j, len(videos_dict)))
                print (fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s)" % (chap))
                chapter_path = course_path + '\\' + chap if os.name == 'nt' else course_path + '/' + chap
                try:
                    os.makedirs(chapter_path)
                except  Exception as e:
                    pass
                chapter_path = course_name + '\\' + chap if os.name == 'nt' else course_name + '/' + chap
                if os.path.exists(chapter_path):
                    os.chdir(chapter_path)
                print (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fc + sd + "Found ('%s') lecture(s)." % (len(videos_dict[chap])))
                i = 1
                for lecture_name,urls in sorted(videos_dict[chap].items()):
                    try:
                        _file           = urls.get('file')
                        _external_url   = urls.get('external_url')
                        _subtitle       = urls.get('subtitle')
                        _view_html      = urls.get('view_html')
                    except AttributeError as e:
                        pass
                    else:
                        if _file and not _external_url and not _subtitle and not _view_html:
                            _url = _file
                        elif _subtitle and not _file and not _external_url and not _view_html:
                            _url = _subtitle
                        elif _view_html and not _subtitle and not _file and not _external_url:
                            _url    =  'html_content'
                        elif not _external_url and not _file and not _subtitle and not _view_html:
                            if not quality:
                                try:
                                    _url = max(urls, key=urls.get)
                                except ValueError as e:
                                    continue
                            else:
                                found = False
                                for url,res in urls.items():
                                    if res == quality:
                                        _url = url
                                        found = True
                                    else:
                                        continue
                                    
                                if not found:
                                    if default:
                                        print (fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Request quality not found for (%s)" % (lecture_name))
                                        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fw + sb + "Downloading default quality...")
                                        try:
                                            _url = max(urls, key=urls.get)
                                        except ValueError as e:
                                            continue
                                    else:
                                        print (fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Request quality is not available for (%s)" % (lecture_name))
                                        if version_info[:2] >= (3, 0):
                                            askUser = input(fc + sd + "[" + fw + sb + "?" + fc + sd + "] : " + fw + sb + "Would you like to download the default quality : ")
                                        else:
                                            askUser = raw_input(fc + sd + "[" + fw + sb + "?" + fc + sd + "] : " + fw + sb + "Would you like to download the default quality : ")
                                        if askUser == 'y' or askUser == 'Y' or askUser == '':
                                            try:
                                                _url = max(urls, key=urls.get)
                                            except ValueError as e:
                                                continue
                                        else:
                                            i += 1
                                            print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Continuing to check for the next lecture..")
                                            continue
                    if _external_url and not _file:
                        _url = _external_url
                        _external_links = "external_links.txt"
                        print (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Saving external links to file : {}".format(_external_links))
                        f = open(_external_links, "a")
                        f.write("- {}\n- {}\n".format(lecture_name.encode("utf-8").strip(), _url.encode("utf-8").strip()))
                        f.close()
                        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Saved successfully..")
                    elif _url != 'html_content':
                        if caption_only and not skip_captions:
                            _suburl = urls.get('subtitle')
                            if _suburl == _url:
                                print (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading subtitle .. ")
                                print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading (%s)" % (lecture_name))
                                msg = self.Downloader(_url, lecture_name, chapter_path)
                                if msg == 'already downloaded':
                                    print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : '%s' " % (lecture_name) + fy + sb + "(already downloaded).")
                                    _is_converted = vtt2srt.convert(lecture_name)
                                elif msg == 'download':
                                    print (fc + sd + "\n[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Downloaded  (%s)" % (lecture_name))
                                    _is_converted = vtt2srt.convert(lecture_name)
                                else:
                                    print (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "{}".format(msg))
                            else:
                                pass
                        elif skip_captions and not caption_only:
                            _suburl = urls.get('subtitle')
                            if _suburl != _url:
                                print (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading lecture : (%s of %s)" % (i, len(videos_dict[chap])))
                                print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading (%s)" % (lecture_name))
                                msg = self.Downloader(_url, lecture_name, chapter_path)
                                if msg == 'already downloaded':
                                    print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : '%s' " % (lecture_name) + fy + sb + "(already downloaded).")
                                elif msg == 'download':
                                    print (fc + sd + "\n[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Downloaded  (%s)" % (lecture_name))
                                else:
                                    print (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "{}".format(msg))
                            else:
                                pass
                        else:
                            print (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading lecture : (%s of %s)" % (i, len(videos_dict[chap])))
                            print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading (%s)" % (lecture_name))
                            msg = self.Downloader(_url, lecture_name, chapter_path)
                            if msg == 'already downloaded':
                                print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : '%s' " % (lecture_name) + fy + sb + "(already downloaded).")
                                if 'vtt' in lecture_name and lecture_name.endswith('.vtt'):
                                    _is_converted = vtt2srt.convert(lecture_name)
                            elif msg == 'download':
                                print (fc + sd + "\n[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Downloaded  (%s)" % (lecture_name))
                                if 'vtt' in lecture_name and lecture_name.endswith('.vtt'):
                                    _is_converted = vtt2srt.convert(lecture_name)
                            else:
                                print (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "{}".format(msg))
                        i += 1
                    elif _url == 'html_content':
                        print (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : (%s)" % (lecture_name))
                        _view_html = (''.join([raw if ord(raw) < 128 else '' for raw in _view_html]))
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
                        ''' % (lecture_name, _view_html)
                        html        = data.encode('utf-8').strip()
                        filename    = '{}.html'.format(lecture_name)
                        if os.path.isfile(filename):
                            print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : '%s' " % (lecture_name) + fy + sb + "(already downloaded).")
                        else:
                            with open(filename, 'wb') as f:
                                f.write(html)
                            f.close
                            print (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Lecture : (%s) " % (lecture_name) + fw + sb + "(saved).")
                        
                j += 1
                print ('')
                os.chdir(current_dir)
                
        



def main():
    ban = banner()
    print (ban)
    usage       = '''%prog [-h] [-u "username"] [-p "password"] COURSE_URL
                   [-s] [-l] [-r "resolution"] [-o "/path/to/directory/"] 
                   [-d] [-c/--configs] [--sub-only] [--skip-sub]'''
    version     = "%prog version {}".format(__version__)
    description = 'A cross-platform python based utility to download courses from udemy for personal offline use.'
    parser = optparse.OptionParser(usage=usage,version=version,conflict_handler="resolve", description=description)

    general = optparse.OptionGroup(parser, 'General')
    general.add_option(
        '-h', '--help',
        action='help',
        help='Shows the help.')
    general.add_option(
        '-v', '--version',
        action='version',
    help='Shows the version.')

    downloader = optparse.OptionGroup(parser, "Advance")
    downloader.add_option(
        "-u", "--username", 
        action='store_true',
        dest='email',\
        help="Username in udemy.")
    downloader.add_option(
        "-p", "--password", 
        action='store_true',
        dest='password',\
        help="Password of your account.")
    downloader.add_option(
        "-c","--configs", 
        action='store_true',
        dest='configurations',\
        help="Cache your credentials to use it later.")
    downloader.add_option(
        "-s", "--save-links", 
        action='store_true',
        dest='save_links',\
        help="Do not download but save links to a file.")
    downloader.add_option(
        "-l", "--list-infos", 
        action='store_true',
        dest='list',\
        help="List all lectures with available resolution.")
    downloader.add_option(
        "-r", "--resolution", 
        action='store_true',
        dest='quality',\
        help="Download video resolution, default resolution is 720p.")
    downloader.add_option(
        "-d", "--get-default", 
        action='store_true',
        default = False,
        dest='default',\
        help="Download default resolution if requested not there.")
    downloader.add_option(
        "-o", "--output", 
        action='store_true',
        dest='output',\
        help="Output directory where the videos will be saved, default is current directory.")

    other   = optparse.OptionGroup(parser, "Others")
    other.add_option(
        "--sub-only", 
        action='store_true',
        dest='caption_only',\
        default=False,\
        help="Download captions/subtitle only.")
    other.add_option(
        "--skip-sub", 
        action='store_true',
        dest='skip_captions',\
        default=False,\
        help="Download course but skip captions/subtitle.")
    

    parser.add_option_group(general)
    parser.add_option_group(downloader)
    parser.add_option_group(other)

    (options, args) = parser.parse_args()

    if not options.email and not options.password:
        try:
            url     = args[0]
        except IndexError as e:
            parser.print_help()
        else:
            config       = use_cached_creds()
            if isinstance(config, dict):
                email       = config.get('username')
                passwd      = config.get('password')
                resolution  = config.get('resolution') or None
                output      = config.get('output') or None

                if resolution != "" and resolution != None:
                    options.quality = True
                    options.default = True
                else:
                    options.quality = False

                if output != "" and output != None:
                    options.output  = True
                else:
                    options.output  = False

                print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Using cached configurations..")
                if email != "" and passwd != "":
                    udemy =  UdemyDownload(url, email, passwd)
                else:
                    print (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Username and password seems empty in 'configuration' file")
                    username = fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Username : " + fg + sb
                    password = fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Password : " + fc + sb
                    email   = getpass.getuser(prompt=username)
                    passwd  = getpass.getpass(prompt=password)
                    print ("")
                    if email and passwd:
                        udemy =  UdemyDownload(url, email, passwd)
                    else:
                        print (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Username and password is required..")
                        exit(0)
                if options.configurations:
                    pass


                '''     Download course      '''

                if not options.save_links and not options.list and not options.output and not options.quality and not options.caption_only and not options.skip_captions:
                    udemy.ExtractAndDownload()
                elif options.caption_only and not options.save_links and not options.list and not options.output and not options.quality and not options.skip_captions:
                    udemy.ExtractAndDownload(caption_only=True)
                elif options.skip_captions and not options.save_links and not options.list and not options.output and not options.quality and not options.caption_only:
                    udemy.ExtractAndDownload(skip_captions=True)

                    '''   Saving course to user define path instead of current directory '''


                elif not options.save_links and not options.list and options.output and not options.quality and not options.caption_only and not options.skip_captions:
                    outto   = args[3]
                    udemy.ExtractAndDownload(path=outto)
                elif options.skip_captions and not options.save_links and not options.list and options.output and not options.quality and not options.caption_only:
                    outto   = args[3]
                    udemy.ExtractAndDownload(path=outto, skip_captions=True)
                elif options.caption_only and not options.save_links and not options.list and options.output and not options.quality and not options.skip_captions:
                    outto   = args[3]
                    udemy.ExtractAndDownload(path=outto, caption_only=True)

                    ''' Saving course to user define path with user define resolution  '''

                elif not options.save_links and not options.list and options.output and options.quality and not options.caption_only and not options.skip_captions:
                    res     = args[3]
                    outto   = args[4]
                    if options.default:
                        udemy.ExtractAndDownload(path=outto, quality=res, default=True)
                    else:
                        udemy.ExtractAndDownload(path=outto, quality=res)
                elif options.caption_only and not options.save_links and not options.list and options.output and options.quality  and not options.skip_captions:
                    res     = args[3]
                    outto   = args[4]
                    if options.default:
                        udemy.ExtractAndDownload(path=outto, quality=res, default=True, caption_only=True)
                    else:
                        udemy.ExtractAndDownload(path=outto, quality=res, caption_only=True)
                elif options.skip_captions and not options.save_links and not options.list and options.output and options.quality and not options.caption_only:
                    res     = args[3]
                    outto   = args[4]
                    if options.default:
                        udemy.ExtractAndDownload(path=outto, quality=res, default=True, skip_captions=True)
                    else:
                        udemy.ExtractAndDownload(path=outto, quality=res, skip_captions=True)

                    ''' Saving course with user define resolution  '''

                elif not options.save_links and not options.list and not options.output and options.quality and not options.caption_only and not options.skip_captions:
                    res     = args[3]
                    if options.default:
                        udemy.ExtractAndDownload(quality=res, default=True)
                    else:
                        udemy.ExtractAndDownload(quality=res)
                elif options.caption_only and not options.save_links and not options.list and not options.output and options.quality and not options.skip_captions:
                    res     = args[3]
                    if options.default:
                        udemy.ExtractAndDownload(quality=res, default=True, caption_only=True)
                    else:
                        udemy.ExtractAndDownload(quality=res, caption_only=True)
                elif options.skip_captions and not options.save_links and not options.list and not options.output and options.quality and not options.caption_only:
                    res     = args[3]
                    if options.default:
                        udemy.ExtractAndDownload(quality=res, default=True, skip_captions=True)
                    else:
                        udemy.ExtractAndDownload(quality=res, skip_captions=True)


                    ''' Save course links '''


                elif options.save_links and not options.list and not options.output and not options.quality:
                    udemy.SaveLinks()
                elif options.save_links and not options.list and not options.output and options.quality:
                    res     = resolution
                    if options.default:
                        udemy.SaveLinks(quality=res, default=True)
                    else:
                        udemy.SaveLinks(quality=res)
                elif options.save_links and not options.list and options.output and not options.quality:
                    outto   = output
                    udemy.SaveLinks(path=outto)
                elif options.save_links and not options.list and options.output and options.quality:
                    res     = resolution
                    outto   = output
                    if options.default:
                        udemy.SaveLinks(quality=res, path=outto, default=True)
                    else:
                        udemy.SaveLinks(quality=res, path=outto)


                    ''' list down available formats of files and videos '''


                elif options.list:
                    udemy.ListDown()

            else:
                username = fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Username : " + fg + sb
                password = fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Password : " + fc + sb
                email   = getpass.getuser(prompt=username)
                passwd  = getpass.getpass(prompt=password)
                print ("")
                if options.configurations:
                    print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Caching configuration...")
                    cached = cache_creds(email, passwd)
                    if cached == 'cached':
                        print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Configurations cached successfully...")

                if email and passwd:
                    udemy =  UdemyDownload(url, email, passwd)
                else:
                    print (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Username and password is required..")
                    exit(0)


                '''     Download course      '''


                if not options.save_links and not options.list and not options.output and not options.quality and not options.caption_only and not options.skip_captions:
                    udemy.ExtractAndDownload()
                elif options.caption_only and not options.save_links and not options.list and not options.output and not options.quality and not options.skip_captions:
                    udemy.ExtractAndDownload(caption_only=True)
                elif options.skip_captions and not options.save_links and not options.list and not options.output and not options.quality and not options.caption_only:
                    udemy.ExtractAndDownload(skip_captions=True)

                    '''   Saving course to user define path instead of current directory '''


                elif not options.save_links and not options.list and options.output and not options.quality and not options.caption_only and not options.skip_captions:
                    outto   = args[1]
                    udemy.ExtractAndDownload(path=outto)
                elif options.skip_captions and not options.save_links and not options.list and options.output and not options.quality and not options.caption_only:
                    outto   = args[1]
                    udemy.ExtractAndDownload(path=outto, skip_captions=True)
                elif options.caption_only and not options.save_links and not options.list and options.output and not options.quality and not options.skip_captions:
                    outto   = args[1]
                    udemy.ExtractAndDownload(path=outto, caption_only=True)

                    ''' Saving course to user define path with user define resolution  '''

                elif not options.save_links and not options.list and options.output and options.quality and not options.caption_only and not options.skip_captions:
                    res     = args[1]
                    outto   = args[2]
                    if options.default:
                        udemy.ExtractAndDownload(path=outto, quality=res, default=True)
                    else:
                        udemy.ExtractAndDownload(path=outto, quality=res)
                elif options.caption_only and not options.save_links and not options.list and options.output and options.quality  and not options.skip_captions:
                    res     = args[1]
                    outto   = args[2]
                    if options.default:
                        udemy.ExtractAndDownload(path=outto, quality=res, default=True, caption_only=True)
                    else:
                        udemy.ExtractAndDownload(path=outto, quality=res, caption_only=True)
                elif options.skip_captions and not options.save_links and not options.list and options.output and options.quality and not options.caption_only:
                    res     = args[1]
                    outto   = args[2]
                    if options.default:
                        udemy.ExtractAndDownload(path=outto, quality=res, default=True, skip_captions=True)
                    else:
                        udemy.ExtractAndDownload(path=outto, quality=res, skip_captions=True)

                    ''' Saving course with user define resolution  '''

                elif not options.save_links and not options.list and not options.output and options.quality and not options.caption_only and not options.skip_captions:
                    res     = args[1]
                    if options.default:
                        udemy.ExtractAndDownload(quality=res, default=True)
                    else:
                        udemy.ExtractAndDownload(quality=res)
                elif options.caption_only and not options.save_links and not options.list and not options.output and options.quality and not options.skip_captions:
                    res     = args[1]
                    if options.default:
                        udemy.ExtractAndDownload(quality=res, default=True, caption_only=True)
                    else:
                        udemy.ExtractAndDownload(quality=res, caption_only=True)
                elif options.skip_captions and not options.save_links and not options.list and not options.output and options.quality and not options.caption_only:
                    res     = args[1]
                    if options.default:
                        udemy.ExtractAndDownload(quality=res, default=True, skip_captions=True)
                    else:
                        udemy.ExtractAndDownload(quality=res, skip_captions=True)


                    ''' Save course links '''


                elif options.save_links and not options.list and not options.output and not options.quality:
                    udemy.SaveLinks()
                elif options.save_links and not options.list and not options.output and options.quality:
                    res     = args[1]
                    if options.default:
                        udemy.SaveLinks(quality=res, default=True)
                    else:
                        udemy.SaveLinks(quality=res)
                elif options.save_links and not options.list and options.output and not options.quality:
                    outto   = args[1]
                    udemy.SaveLinks(path=outto)
                elif options.save_links and not options.list and options.output and options.quality:
                    res     = args[1]
                    outto   = args[2]
                    if options.default:
                        udemy.SaveLinks(quality=res, path=outto, default=True)
                    else:
                        udemy.SaveLinks(quality=res, path=outto)


                    ''' list down available formats of files and videos '''


                elif not options.save_links and options.list and not options.output and not options.quality:
                    udemy.ListDown()

    elif options.email and options.password:
        email       = args[0]
        passwd      = args[1] 
        try:
            url     = args[2] 
        except IndexError as e:
            parser.print_usage()
        else:
            if options.configurations:
                print (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Caching configurations...")
                cached = cache_creds(email, passwd)
                if cached == 'cached':
                    print (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Configurations cached successfully...")

            udemy =  UdemyDownload(url, email, passwd)
            

            '''     Download course      '''


            if not options.save_links and not options.list and not options.output and not options.quality and not options.caption_only and not options.skip_captions:
                udemy.ExtractAndDownload()
            elif options.caption_only and not options.save_links and not options.list and not options.output and not options.quality and not options.skip_captions:
                udemy.ExtractAndDownload(caption_only=True)
            elif options.skip_captions and not options.save_links and not options.list and not options.output and not options.quality and not options.caption_only:
                udemy.ExtractAndDownload(skip_captions=True)

                '''   Saving course to user define path instead of current directory '''


            elif not options.save_links and not options.list and options.output and not options.quality and not options.caption_only and not options.skip_captions:
                outto   = args[3]
                udemy.ExtractAndDownload(path=outto)
            elif options.skip_captions and not options.save_links and not options.list and options.output and not options.quality and not options.caption_only:
                outto   = args[3]
                udemy.ExtractAndDownload(path=outto, skip_captions=True)
            elif options.caption_only and not options.save_links and not options.list and options.output and not options.quality and not options.skip_captions:
                outto   = args[3]
                udemy.ExtractAndDownload(path=outto, caption_only=True)

                ''' Saving course to user define path with user define resolution  '''

            elif not options.save_links and not options.list and options.output and options.quality and not options.caption_only and not options.skip_captions:
                res     = args[3]
                outto   = args[4]
                if options.default:
                    udemy.ExtractAndDownload(path=outto, quality=res, default=True)
                else:
                    udemy.ExtractAndDownload(path=outto, quality=res)
            elif options.caption_only and not options.save_links and not options.list and options.output and options.quality  and not options.skip_captions:
                res     = args[3]
                outto   = args[4]
                if options.default:
                    udemy.ExtractAndDownload(path=outto, quality=res, default=True, caption_only=True)
                else:
                    udemy.ExtractAndDownload(path=outto, quality=res, caption_only=True)
            elif options.skip_captions and not options.save_links and not options.list and options.output and options.quality and not options.caption_only:
                res     = args[3]
                outto   = args[4]
                if options.default:
                    udemy.ExtractAndDownload(path=outto, quality=res, default=True, skip_captions=True)
                else:
                    udemy.ExtractAndDownload(path=outto, quality=res, skip_captions=True)

                ''' Saving course with user define resolution  '''

            elif not options.save_links and not options.list and not options.output and options.quality and not options.caption_only and not options.skip_captions:
                res     = args[3]
                if options.default:
                    udemy.ExtractAndDownload(quality=res, default=True)
                else:
                    udemy.ExtractAndDownload(quality=res)
            elif options.caption_only and not options.save_links and not options.list and not options.output and options.quality and not options.skip_captions:
                res     = args[3]
                if options.default:
                    udemy.ExtractAndDownload(quality=res, default=True, caption_only=True)
                else:
                    udemy.ExtractAndDownload(quality=res, caption_only=True)
            elif options.skip_captions and not options.save_links and not options.list and not options.output and options.quality and not options.caption_only:
                res     = args[3]
                if options.default:
                    udemy.ExtractAndDownload(quality=res, default=True, skip_captions=True)
                else:
                    udemy.ExtractAndDownload(quality=res, skip_captions=True)

                ''' Save course links '''


            elif options.save_links and not options.list and not options.output and not options.quality:
                udemy.SaveLinks()
            elif options.save_links and not options.list and not options.output and options.quality:
                res     = args[3]
                if options.default:
                    udemy.SaveLinks(quality=res, default=True)
                else:
                    udemy.SaveLinks(quality=res)
            elif options.save_links and not options.list and options.output and not options.quality:
                outto   = args[3]
                udemy.SaveLinks(path=outto)
            elif options.save_links and not options.list and options.output and options.quality:
                res     = args[3]
                outto   = args[4]
                if options.default:
                    udemy.SaveLinks(quality=res, path=outto, default=True)
                else:
                    udemy.SaveLinks(quality=res, path=outto)


                ''' list down available formats of files and videos '''


            elif not options.save_links and options.list and not options.output and not options.quality:
                udemy.ListDown()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print (fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..")
        time.sleep(0.8)
    except IndexError:
        print (fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "Username, Password and course url is required..")
