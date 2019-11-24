#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import udemy
import codecs
import argparse

from pprint import pprint
from udemy import __version__
from udemy._colorized import *
from udemy._compat import pyver
from udemy._getpass import GetPass
from udemy._vtt2srt import WebVtt2Srt
from udemy._progress import ProgressBar
from udemy._colorized.banner import banner
from udemy._utils import cache_credentials
from udemy._utils import use_cached_credentials
getpass = GetPass()


class Udemy(WebVtt2Srt, ProgressBar):

    def __init__(self, url, username='', password='', cookies=''):
        self.url        =   url
        self.username   =   username
        self.password   =   password
        self.cookies    =   cookies
        super(Udemy, self).__init__()

    def _write_to_file(self, filepath='', lecture='', names_only=False, unsafe=False):
        retVal = {}
        filename = filepath
        filename += '-names-only.txt' if names_only else ".txt"
        fmode = "a"
        if not unsafe:
            title = lecture.title
            url = lecture.url
            url_or_name = url if not names_only else title
            url_or_name += "\n"
        if unsafe:
            title = u'%s' % (lecture.unsafe_title)
            url = lecture.url
            url_or_name = url if not names_only else title
            url_or_name += "\n"

        try:
            f = codecs.open(filename, fmode, encoding='utf-8', errors='ignore')
            f.write(url_or_name)
        except (OSError, Exception, UnicodeDecodeError) as e:
            retVal = {'status' : 'False', 'msg' : '{}'.format(e)}
        else:
            retVal = {'status' : 'True', 'msg' : 'download'}
            f.close()

        return retVal

    def course_save(self, path='', quality='', caption_only=False, skip_captions=False, names_only=False, unsafe=False):
        if not self.cookies:
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to login as " + fm + sb +"(%s)" % (self.username) +  fg + sb +"...\n")
        if self.cookies:
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to login using cookies ...\n")
        course = udemy.course(url=self.url, username=self.username, password=self.password, cookies=self.cookies)
        course_id = course.id
        course_name = course.title
        total_lectures = course.lectures
        total_chapters = course.chapters
        course_name = (course_name.lower()).replace(' ', '-')
        chapters = course.get_chapters()
        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Course " + fb + sb + "'%s'.\n" % (course_name))
        sys.stdout.write (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Chapter(s) (%s).\n" % (total_chapters))
        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (total_lectures))
        if path:
            if '~' in path:
                path    = os.path.expanduser(path)
            course_path    = "%s\\%s" % (path, course_name) if os.name == 'nt' else "%s/%s" % (path, course_name)
        else:
            path        = os.getcwd()
            course_path = "%s\\%s" % (path, course_name) if os.name == 'nt' else "%s/%s" % (path, course_name)
        filepath = '%s.txt' % (course_path)
        if os.path.isfile(filepath):
            with open(filepath, 'w') as f:
                f.close()
        if not names_only:
            sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Writing course content(s) to '%s.txt'\n" % (course_name))
        if names_only:
            sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Writing course lecture names to '%s-names-only.txt'\n" % (course_name))
        for chapter in chapters:
            chapter_id = chapter.id
            chapter_title = chapter.title
            lectures = chapter.get_lectures()
            lectures_count = chapter.lectures
            for lecture in lectures:
                lecture_id = lecture.id
                lecture_streams = lecture.streams
                lecture_best = lecture.getbest()
                lecture_assets = lecture.assets
                lecture_subtitles = lecture.subtitles
                if quality:
                    index = 0
                    while index < len(lecture_streams):
                        dimension = int(lecture_streams[index].dimention[1])
                        if dimension == quality:
                            lecture_best = lecture_streams[index]
                            break
                        index += 1
                    if not lecture_best:
                        lecture_best = lecture_best
                if caption_only and not skip_captions:
                    if lecture_subtitles:
                        for subtitle in lecture_subtitles:
                            self._write_to_file(filepath=course_path, lecture=subtitle, names_only=names_only, unsafe=unsafe)
                    if lecture_assets:
                        for asset in lecture_assets:
                            self._write_to_file(filepath=course_path, lecture=asset, names_only=names_only, unsafe=unsafe)
                elif skip_captions and not caption_only:
                    if lecture_best:
                        self._write_to_file(filepath=course_path, lecture=lecture_best, names_only=names_only, unsafe=unsafe)
                    if lecture_assets:
                        for asset in lecture_assets:
                            self._write_to_file(filepath=course_path, lecture=asset, names_only=names_only, unsafe=unsafe)
                else:
                    if lecture_best:
                        self._write_to_file(filepath=course_path, lecture=lecture_best, names_only=names_only, unsafe=unsafe)
                    if lecture_assets:
                        for asset in lecture_assets:
                            self._write_to_file(filepath=course_path, lecture=asset, names_only=names_only, unsafe=unsafe)
                    if lecture_subtitles:
                        for subtitle in lecture_subtitles:
                            self._write_to_file(filepath=course_path, lecture=subtitle, names_only=names_only, unsafe=unsafe)
        if not names_only:
            sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Written successfully under '{name}.txt'.\n".format(name=course_path))
        if names_only:
            sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Written successfully under '{name}-names-only.txt'.\n".format(name=course_path))

    def course_list_down(self, chapter_number='', lecture_number='', unsafe=False):
        if not self.cookies:
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to login as " + fm + sb +"(%s)" % (self.username) +  fg + sb +"...\n")
        if self.cookies:
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to login using cookies ...\n")
        course = udemy.course(url=self.url, username=self.username, password=self.password, cookies=self.cookies)
        course_id = course.id
        course_name = course.title
        total_lectures = course.lectures
        total_chapters = course.chapters
        chapters = course.get_chapters()
        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Course " + fb + sb + "'%s'.\n" % (course_name))
        sys.stdout.write (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Chapter(s) (%s).\n" % (total_chapters))
        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (total_lectures))
        if chapter_number and chapter_number > 0 and chapter_number <= total_chapters:
            chapter = chapters[chapter_number-1]
            chapter_id = chapter.id
            chapter_title = chapter.title if not unsafe else "%02d" % (int(chapter.index))
            lectures = chapter.get_lectures()
            lectures_count = chapter.lectures
            sys.stdout.write ('\n' + fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s-%s)\n" % (chapter_title, chapter_id))
            sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (lectures_count))
            if lecture_number and lecture_number > 0 and lecture_number <= lectures_count:
                lecture = lectures[lecture_number-1]
                lecture_id = lecture.id
                lecture_streams = lecture.streams
                lecture_best = lecture.getbest()
                lecture_assets = lecture.assets
                lecture_subtitles = lecture.subtitles
                if lecture_streams:
                    sys.stdout.write(fc + sd + "     - " + fy + sb + "duration   : " + fm + sb + str(lecture.duration)+ fy + sb + ".\n")
                    sys.stdout.write(fc + sd + "     - " + fy + sb + "Lecture id : " + fm + sb + str(lecture_id)+ fy + sb + ".\n")
                    for stream in lecture_streams:
                        content_length = stream.get_filesize()
                        if content_length != 0:
                            if content_length <= 1048576.00:
                                size = round(float(content_length) / 1024.00, 2)
                                sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                in_MB = 'KB' if size < 1024.00 else 'MB'
                            else:
                                size = round(float(content_length) / 1048576, 2)
                                sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                in_MB = "MB " if size < 1024.00 else 'GB '
                            if lecture_best.dimention[1] == stream.dimention[1]:
                                in_MB = in_MB + fc + sb + "(Best)" + fg + sd
                            sys.stdout.write('\t- ' + fg + sd + "{:<22} {:<8}{}{}{}{}\n".format(str(stream), stream.dimention[1] + 'p', sz, in_MB, fy, sb))
                if lecture_assets:
                    for asset in lecture_assets:
                        if asset.mediatype != 'external_link':
                            content_length = asset.get_filesize()
                            if content_length != 0:
                                if content_length <= 1048576.00:
                                    size = round(float(content_length) / 1024.00, 2)
                                    sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                    in_MB = 'KB' if size < 1024.00 else 'MB'
                                else:
                                    size = round(float(content_length) / 1048576, 2)
                                    sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                    in_MB = "MB " if size < 1024.00 else 'GB '
                                sys.stdout.write('\t- ' + fg + sd + "{:<22} {:<8}{}{}{}{}\n".format(str(asset), asset.extension, sz, in_MB, fy, sb))
                if lecture_subtitles:
                    for subtitle in lecture_subtitles:
                        content_length = subtitle.get_filesize()
                        if content_length != 0:
                            if content_length <= 1048576.00:
                                size = round(float(content_length) / 1024.00, 2)
                                sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                in_MB = 'KB' if size < 1024.00 else 'MB'
                            else:
                                size = round(float(content_length) / 1048576, 2)
                                sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                in_MB = "MB " if size < 1024.00 else 'GB '
                            sys.stdout.write('\t- ' + fg + sd + "{:<22} {:<8}{}{}{}{}\n".format(str(subtitle), subtitle.extension, sz, in_MB, fy, sb))
            else:
                for lecture in lectures:
                    lecture_id = lecture.id
                    lecture_streams = lecture.streams
                    lecture_best = lecture.getbest()
                    lecture_assets = lecture.assets
                    lecture_subtitles = lecture.subtitles
                    if lecture_streams:
                        sys.stdout.write(fc + sd + "     - " + fy + sb + "duration   : " + fm + sb + str(lecture.duration)+ fy + sb + ".\n")
                        sys.stdout.write(fc + sd + "     - " + fy + sb + "Lecture id : " + fm + sb + str(lecture_id)+ fy + sb + ".\n")
                        for stream in lecture_streams:
                            content_length = stream.get_filesize()
                            if content_length != 0:
                                if content_length <= 1048576.00:
                                    size = round(float(content_length) / 1024.00, 2)
                                    sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                    in_MB = 'KB' if size < 1024.00 else 'MB'
                                else:
                                    size = round(float(content_length) / 1048576, 2)
                                    sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                    in_MB = "MB " if size < 1024.00 else 'GB '
                                if lecture_best.dimention[1] == stream.dimention[1]:
                                    in_MB = in_MB + fc + sb + "(Best)" + fg + sd
                                sys.stdout.write('\t- ' + fg + sd + "{:<22} {:<8}{}{}{}{}\n".format(str(stream), stream.dimention[1] + 'p', sz, in_MB, fy, sb))
                    if lecture_assets:
                        for asset in lecture_assets:
                            if asset.mediatype != 'external_link':
                                content_length = asset.get_filesize()
                                if content_length != 0:
                                    if content_length <= 1048576.00:
                                        size = round(float(content_length) / 1024.00, 2)
                                        sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                        in_MB = 'KB' if size < 1024.00 else 'MB'
                                    else:
                                        size = round(float(content_length) / 1048576, 2)
                                        sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                        in_MB = "MB " if size < 1024.00 else 'GB '
                                    sys.stdout.write('\t- ' + fg + sd + "{:<22} {:<8}{}{}{}{}\n".format(str(asset), asset.extension, sz, in_MB, fy, sb))
                    if lecture_subtitles:
                        for subtitle in lecture_subtitles:
                            content_length = subtitle.get_filesize()
                            if content_length != 0:
                                if content_length <= 1048576.00:
                                    size = round(float(content_length) / 1024.00, 2)
                                    sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                    in_MB = 'KB' if size < 1024.00 else 'MB'
                                else:
                                    size = round(float(content_length) / 1048576, 2)
                                    sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                    in_MB = "MB " if size < 1024.00 else 'GB '
                                sys.stdout.write('\t- ' + fg + sd + "{:<22} {:<8}{}{}{}{}\n".format(str(subtitle), subtitle.extension, sz, in_MB, fy, sb))
        else:
            for chapter in chapters:
                chapter_id = chapter.id
                chapter_title = chapter.title if not unsafe else "%02d" % (int(chapter.index))
                lectures = chapter.get_lectures()
                lectures_count = chapter.lectures
                sys.stdout.write ('\n' + fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s-%s)\n" % (chapter_title, chapter_id))
                sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (lectures_count))
                for lecture in lectures:
                    lecture_id = lecture.id
                    lecture_streams = lecture.streams
                    lecture_best = lecture.getbest()
                    lecture_assets = lecture.assets
                    lecture_subtitles = lecture.subtitles
                    if lecture_streams:
                        sys.stdout.write(fc + sd + "     - " + fy + sb + "duration   : " + fm + sb + str(lecture.duration)+ fy + sb + ".\n")
                        sys.stdout.write(fc + sd + "     - " + fy + sb + "Lecture id : " + fm + sb + str(lecture_id)+ fy + sb + ".\n")
                        for stream in lecture_streams:
                            content_length = stream.get_filesize()
                            if content_length != 0:
                                if content_length <= 1048576.00:
                                    size = round(float(content_length) / 1024.00, 2)
                                    sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                    in_MB = 'KB' if size < 1024.00 else 'MB'
                                else:
                                    size = round(float(content_length) / 1048576, 2)
                                    sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                    in_MB = "MB " if size < 1024.00 else 'GB '
                                if lecture_best.dimention[1] == stream.dimention[1]:
                                    in_MB = in_MB + fc + sb + "(Best)" + fg + sd
                                sys.stdout.write('\t- ' + fg + sd + "{:<22} {:<8}{}{}{}{}\n".format(str(stream), stream.dimention[1] + 'p', sz, in_MB, fy, sb))
                    if lecture_assets:
                        for asset in lecture_assets:
                            if asset.mediatype != 'external_link':
                                content_length = asset.get_filesize()
                                if content_length != 0:
                                    if content_length <= 1048576.00:
                                        size = round(float(content_length) / 1024.00, 2)
                                        sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                        in_MB = 'KB' if size < 1024.00 else 'MB'
                                    else:
                                        size = round(float(content_length) / 1048576, 2)
                                        sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                        in_MB = "MB " if size < 1024.00 else 'GB '
                                    sys.stdout.write('\t- ' + fg + sd + "{:<22} {:<8}{}{}{}{}\n".format(str(asset), asset.extension, sz, in_MB, fy, sb))
                    if lecture_subtitles:
                        for subtitle in lecture_subtitles:
                            content_length = subtitle.get_filesize()
                            if content_length != 0:
                                if content_length <= 1048576.00:
                                    size = round(float(content_length) / 1024.00, 2)
                                    sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                    in_MB = 'KB' if size < 1024.00 else 'MB'
                                else:
                                    size = round(float(content_length) / 1048576, 2)
                                    sz = format(size if size < 1024.00 else size/1024.00, '.2f')
                                    in_MB = "MB " if size < 1024.00 else 'GB '
                                sys.stdout.write('\t- ' + fg + sd + "{:<22} {:<8}{}{}{}{}\n".format(str(subtitle), subtitle.extension, sz, in_MB, fy, sb))

    def download_assets(self, lecture_assets='', filepath='', unsafe=False):
        if lecture_assets:
            for assets in lecture_assets:
                title = assets.filename if not unsafe else "%s" % (assets)
                mediatype = assets.mediatype
                if mediatype == "external_link":
                    assets.download(filepath=filepath, unsafe=unsafe, quiet=True, callback=self.show_progress)
                else:
                    sys.stdout.write(fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading asset(s)\n")
                    sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading (%s)\n" % (title))
                    try:
                        retval = assets.download(filepath=filepath, unsafe=unsafe, quiet=True, callback=self.show_progress)
                    except KeyboardInterrupt:
                        sys.stdout.write (fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                        sys.exit(0)
                    else:
                        msg     = retval.get('msg')
                        if msg == 'already downloaded':
                            sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Asset : '%s' " % (title) + fy + sb + "(already downloaded).\n")
                        elif msg == 'download':
                            sys.stdout.write (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Downloaded  (%s)\n" % (title))
                        else:
                            sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Asset : '%s' " % (title) + fc + sb + "(download skipped).\n")
                            sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "{}\n".format(msg))

    def download_subtitles(self, lecture_subtitles='', language='', filepath='', unsafe=False):
        if language:
            _lecture_subtitles = [i for i in lecture_subtitles if i.language == language]
            if _lecture_subtitles:
                lecture_subtitles = _lecture_subtitles
        if lecture_subtitles:
            for subtitles in lecture_subtitles:
                title = subtitles.title + '-' + subtitles.language if not unsafe else "%s" % (subtitles)
                if not unsafe:
                    filename = "%s\\%s" % (filepath, subtitles.filename) if os.name == 'nt' else "%s/%s" % (filepath, subtitles.filename)
                if unsafe:
                    filename = u"%s\\%s" % (filepath, subtitles.unsafe_filename) if os.name == 'nt' else u"%s/%s" % (filepath, subtitles.unsafe_filename)

                sys.stdout.write(fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading subtitle(s)\n")
                sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading (%s)\n" % (title))
                
                try:
                    retval = subtitles.download(filepath=filepath, unsafe=unsafe, quiet=True, callback=self.show_progress)
                except KeyboardInterrupt:
                    sys.stdout.write (fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                    sys.exit(0)
                else:
                    msg     = retval.get('msg')
                    if msg == 'already downloaded':
                        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Subtitle : '%s' " % (title) + fy + sb + "(already downloaded).\n")
                        self.convert(filename=filename)
                    elif msg == 'download':
                        sys.stdout.write (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Downloaded  (%s)\n" % (title))
                        self.convert(filename=filename)
                    else:
                        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Subtitle : '%s' " % (title) + fc + sb + "(download skipped).\n")
                        sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "{}\n".format(msg))

    def download_lectures(self, lecture_best='', lecture_title='', inner_index='', lectures_count='', filepath='', unsafe=False):
        if lecture_best:
            sys.stdout.write(fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) : ({index} of {total})\n".format(index=inner_index, total=lectures_count))
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading (%s)\n" % (lecture_title))
            try:
                retval = lecture_best.download(filepath=filepath, unsafe=unsafe, quiet=True, callback=self.show_progress)
            except KeyboardInterrupt:
                sys.stdout.write (fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                sys.exit(0)
            else:
                msg     = retval.get('msg')
                if msg == 'already downloaded':
                    if not unsafe:
                        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : '%s' " % (lecture_title) + fy + sb + "(already downloaded).\n")
                    if unsafe:
                        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "'%s' " % (lecture_title) + fy + sb + "(already downloaded).\n")
                elif msg == 'download':
                    sys.stdout.write (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Downloaded  (%s)\n" % (lecture_title))
                else:
                    if not unsafe:
                        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : '%s' " % (lecture_title) + fc + sb + "(download skipped).\n")
                    if unsafe:
                        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "'%s' " % (lecture_title) + fc + sb + "(download skipped).\n")
                    sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "{}\n".format(msg))

    def download_captions_only(self, lecture_subtitles='', language='', lecture_assets='', filepath='', unsafe=False):
        if lecture_subtitles:
            self.download_subtitles(lecture_subtitles=lecture_subtitles, language=language, filepath=filepath, unsafe=unsafe)
        if lecture_assets:
            self.download_assets(lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)

    def download_lectures_only(self, lecture_best='', lecture_title='', inner_index='', lectures_count='', lecture_assets='', filepath='', unsafe=False):
        if lecture_best:
            self.download_lectures(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=inner_index, lectures_count=lectures_count, filepath=filepath, unsafe=unsafe)
        if lecture_assets:
            self.download_assets(lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)

    def download_lectures_and_captions(self, lecture_best='', lecture_title='', inner_index='', lectures_count='', lecture_subtitles='', language='', lecture_assets='', filepath='', unsafe=False):
        if lecture_best:
            self.download_lectures(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=inner_index, lectures_count=lectures_count, filepath=filepath, unsafe=unsafe)
        if lecture_subtitles:
            self.download_subtitles(lecture_subtitles=lecture_subtitles, language=language, filepath=filepath, unsafe=unsafe)
        if lecture_assets:
            self.download_assets(lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)

    def course_download(self, path='', quality='', language='', caption_only=False, skip_captions=False, unsafe=False):
        if not self.cookies:
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to login as " + fm + sb +"(%s)" % (self.username) +  fg + sb +"...\n")
        if self.cookies:
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to login using cookies ...\n")
        course = udemy.course(url=self.url, username=self.username, password=self.password, cookies=self.cookies)
        course_id = course.id
        course_name = course.title
        chapters = course.get_chapters()
        total_lectures = course.lectures
        total_chapters = course.chapters
        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Course " + fb + sb + "'%s'.\n" % (course_name))
        sys.stdout.write (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Chapter(s) (%s).\n" % (total_chapters))
        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (total_lectures))
        if path:
            if '~' in path:
                path    = os.path.expanduser(path)
            course_path    = "%s\\%s" % (path, course_name) if os.name == 'nt' else "%s/%s" % (path, course_name)
        else:
            path        = os.getcwd()
            course_path = "%s\\%s" % (path, course_name) if os.name == 'nt' else "%s/%s" % (path, course_name)
        for chapter in chapters:
            chapter_id = chapter.id
            chapter_index = chapter.index
            chapter_title = chapter.title
            lectures = chapter.get_lectures()
            lectures_count = chapter.lectures
            if unsafe:
                filepath = u"%s\\%s" % (course_path, chapter.unsafe_title) if os.name == 'nt' else u"%s/%s" % (course_path, chapter.unsafe_title)
            if not unsafe:
                filepath = "%s\\%s" % (course_path, chapter_title) if os.name == 'nt' else "%s/%s" % (course_path, chapter_title)
            try:
                os.makedirs(filepath)
            except Exception as e:
                pass
            sys.stdout.write (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fm + sb + "Downloading chapter : ({index} of {total})\n".format(index=chapter_index, total=total_chapters))
            if not unsafe:
                sys.stdout.write (fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s)\n" % (chapter_title))
                sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Found (%s) lectures ...\n" % (lectures_count))
            if unsafe:
                sys.stdout.write (fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%02d-%s)\n" % (int(chapter_index), chapter_id))
                sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (lectures_count))
            inner_index = 1
            for lecture in lectures:
                lecture_id = lecture.id
                lecture_index = lecture.index
                lecture_title = lecture.title if not unsafe else "Lecture id : %s" % (lecture_id)
                lecture_assets = lecture.assets
                lecture_subtitles = lecture.subtitles
                lecture_best = lecture.getbest()
                lecture_streams = lecture.streams
                if caption_only and not skip_captions:
                    self.download_captions_only(lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                elif skip_captions and not caption_only:
                    if quality:
                        index = 0
                        while index < len(lecture_streams):
                            dimension = int(lecture_streams[index].dimention[1])
                            if dimension == quality:
                                lecture_best = lecture_streams[index]
                                break
                            index += 1
                        if not lecture_best:
                            lecture_best = lecture_best
                    if lecture.html:
                        lecture.dump(filepath=filepath, unsafe=unsafe)
                    self.download_lectures_only(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=inner_index, lectures_count=lectures_count, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                else:
                    if quality:
                        index = 0
                        while index < len(lecture_streams):
                            dimension = int(lecture_streams[index].dimention[1])
                            if dimension == quality:
                                lecture_best = lecture_streams[index]
                                break
                            index += 1
                        if not lecture_best:
                            lecture_best = lecture_best
                    if lecture.html:
                        lecture.dump(filepath=filepath, unsafe=unsafe)
                    self.download_lectures_and_captions(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=inner_index, lectures_count=lectures_count, lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                inner_index += 1

    def chapter_download(self, chapter_number='', chapter_start='', chapter_end='', lecture_number='', lecture_start='', lecture_end='', path='', quality='', language='', caption_only=False, skip_captions=False, unsafe=False):
        if not self.cookies:
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to login as " + fm + sb +"(%s)" % (self.username) +  fg + sb +"...\n")
        if self.cookies:
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to login using cookies ...\n")
        course = udemy.course(url=self.url, username=self.username, password=self.password, cookies=self.cookies)
        course_id = course.id
        course_name = course.title
        chapters = course.get_chapters()
        total_lectures = course.lectures
        total_chapters = course.chapters
        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Course " + fb + sb + "'%s'.\n" % (course_name))
        sys.stdout.write (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Chapter(s) (%s).\n" % (total_chapters))
        sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (total_lectures))
        if path:
            if '~' in path:
                path    = os.path.expanduser(path)
            course_path    = "%s\\%s" % (path, course_name) if os.name == 'nt' else "%s/%s" % (path, course_name)
        else:
            path        = os.getcwd()
            course_path = "%s\\%s" % (path, course_name) if os.name == 'nt' else "%s/%s" % (path, course_name)
        _lectures_start, _lectures_end = lecture_start, lecture_end
        if chapter_start and not chapter_end:
            chapter_end = total_chapters
        if chapter_number and chapter_number > 0 and chapter_number <= total_chapters:
            chapter = chapters[chapter_number-1]
            if chapter:
                chapter_id = chapter.id
                chapter_index = chapter.index
                chapter_title = chapter.title
                lectures = chapter.get_lectures()
                lectures_count = chapter.lectures
                if lecture_end and lecture_end > lectures_count:
                    lecture_end = lectures_count

                if unsafe:
                    filepath = u"%s\\%s" % (course_path, chapter.unsafe_title) if os.name == 'nt' else u"%s/%s" % (course_path, chapter.unsafe_title)
                if not unsafe:
                    filepath = "%s\\%s" % (course_path, chapter_title) if os.name == 'nt' else "%s/%s" % (course_path, chapter_title)
                try:
                    os.makedirs(filepath)
                except Exception as e:
                    pass
                sys.stdout.write (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fm + sb + "Downloading chapter : ({index})\n".format(index=chapter_index))
                if not unsafe:
                    sys.stdout.write (fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s)\n" % (chapter_title))
                    sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Found (%s) lectures ...\n" % (lectures_count))
                if unsafe:
                    sys.stdout.write (fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%02d-%s)\n" % (int(chapter_index), chapter_id))
                    sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (lectures_count))
                lecture_start = _lectures_start
                lecture_end = lectures_count if lecture_start and not lecture_end else _lectures_end
                if lecture_number and lecture_number > 0 and lecture_number <= lectures_count:
                    lecture = lectures[lecture_number-1]
                    lecture_id = lecture.id
                    lecture_index = lecture.index
                    lecture_title = lecture.title if not unsafe else "Lecture id : %s" % (lecture_id)
                    lecture_assets = lecture.assets
                    lecture_subtitles = lecture.subtitles
                    lecture_best = lecture.getbest()
                    lecture_streams = lecture.streams
                    if caption_only and not skip_captions:
                        self.download_captions_only(lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                    elif skip_captions and not caption_only:
                        if quality:
                            index = 0
                            while index < len(lecture_streams):
                                dimension = int(lecture_streams[index].dimention[1])
                                if dimension == quality:
                                    lecture_best = lecture_streams[index]
                                    break
                                index += 1
                            if not lecture_best:
                                lecture_best = lecture_best
                        if lecture.html:
                            lecture.dump(filepath=filepath)
                        self.download_lectures_only(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=lecture_number, lectures_count=lectures_count, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                    else:
                        if quality:
                            index = 0
                            while index < len(lecture_streams):
                                dimension = int(lecture_streams[index].dimention[1])
                                if dimension == quality:
                                    lecture_best = lecture_streams[index]
                                    break
                                index += 1
                            if not lecture_best:
                                lecture_best = lecture_best
                        if lecture.html:
                            lecture.dump(filepath=filepath)
                        self.download_lectures_and_captions(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=lecture_number, lectures_count=lectures_count, lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                elif lecture_start and lecture_start > 0 and lecture_start <= lecture_end and lecture_end <= lectures_count:
                    while lecture_start <= lecture_end:
                        lecture = lectures[lecture_start-1]
                        lecture_id = lecture.id
                        lecture_index = lecture.index
                        lecture_title = lecture.title if not unsafe else "Lecture id : %s" % (lecture_id)
                        lecture_assets = lecture.assets
                        lecture_subtitles = lecture.subtitles
                        lecture_best = lecture.getbest()
                        lecture_streams = lecture.streams
                        if caption_only and not skip_captions:
                            self.download_captions_only(lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        elif skip_captions and not caption_only:
                            if quality:
                                index = 0
                                while index < len(lecture_streams):
                                    dimension = int(lecture_streams[index].dimention[1])
                                    if dimension == quality:
                                        lecture_best = lecture_streams[index]
                                        break
                                    index += 1
                                if not lecture_best:
                                    lecture_best = lecture_best
                            if lecture.html:
                                lecture.dump(filepath=filepath, unsafe=unsafe)
                            self.download_lectures_only(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=lecture_start, lectures_count=lecture_end, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        else:
                            if quality:
                                index = 0
                                while index < len(lecture_streams):
                                    dimension = int(lecture_streams[index].dimention[1])
                                    if dimension == quality:
                                        lecture_best = lecture_streams[index]
                                        break
                                    index += 1
                                if not lecture_best:
                                    lecture_best = lecture_best
                            if lecture.html:
                                lecture.dump(filepath=filepath, unsafe=unsafe)
                            self.download_lectures_and_captions(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=lecture_start, lectures_count=lecture_end, lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        lecture_start += 1
                else:
                    inner_index = 1
                    for lecture in lectures:
                        lecture_id = lecture.id
                        lecture_index = lecture.index
                        lecture_title = lecture.title if not unsafe else "Lecture id : %s" % (lecture_id)
                        lecture_assets = lecture.assets
                        lecture_subtitles = lecture.subtitles
                        lecture_best = lecture.getbest()
                        lecture_streams = lecture.streams
                        if caption_only and not skip_captions:
                            self.download_captions_only(lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        elif skip_captions and not caption_only:
                            if quality:
                                index = 0
                                while index < len(lecture_streams):
                                    dimension = int(lecture_streams[index].dimention[1])
                                    if dimension == quality:
                                        lecture_best = lecture_streams[index]
                                        break
                                    index += 1
                                if not lecture_best:
                                    lecture_best = lecture_best
                            if lecture.html:
                                lecture.dump(filepath=filepath, unsafe=unsafe)
                            self.download_lectures_only(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=inner_index, lectures_count=lectures_count, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        else:
                            if quality:
                                index = 0
                                while index < len(lecture_streams):
                                    dimension = int(lecture_streams[index].dimention[1])
                                    if dimension == quality:
                                        lecture_best = lecture_streams[index]
                                        break
                                    index += 1
                                if not lecture_best:
                                    lecture_best = lecture_best
                            if lecture.html:
                                lecture.dump(filepath=filepath, unsafe=unsafe)
                            self.download_lectures_and_captions(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=inner_index, lectures_count=lectures_count, lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        inner_index += 1
        elif chapter_start and chapter_start > 0 and chapter_start <= chapter_end and chapter_end <= total_chapters:
            while chapter_start <= chapter_end:
                chapter = chapters[chapter_start-1]
                chapter_id = chapter.id
                chapter_index = chapter.index
                chapter_title = chapter.title
                lectures = chapter.get_lectures()
                lectures_count = chapter.lectures
                if unsafe:
                    filepath = u"%s\\%s" % (course_path, chapter.unsafe_title) if os.name == 'nt' else u"%s/%s" % (course_path, chapter.unsafe_title)
                if not unsafe:
                    filepath = "%s\\%s" % (course_path, chapter_title) if os.name == 'nt' else "%s/%s" % (course_path, chapter_title)
                try:
                    os.makedirs(filepath)
                except Exception as e:
                    pass
                sys.stdout.write (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fm + sb + "Downloading chapter : ({index} of {total})\n".format(index=chapter_start, total=chapter_end))
                if not unsafe:
                    sys.stdout.write (fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s)\n" % (chapter_title))
                    sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Found (%s) lectures ...\n" % (lectures_count))
                if unsafe:
                    sys.stdout.write (fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%02d-%s)\n" % (int(chapter_index), chapter_id))
                    sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (lectures_count))
                lecture_start = _lectures_start
                lecture_end = lectures_count if lecture_start and not lecture_end else _lectures_end
                if lecture_number and lecture_number > 0 and lecture_number <= lectures_count:
                    lecture = lectures[lecture_number-1]
                    lecture_id = lecture.id
                    lecture_index = lecture.index
                    lecture_title = lecture.title if not unsafe else "Lecture id : %s" % (lecture_id)
                    lecture_assets = lecture.assets
                    lecture_subtitles = lecture.subtitles
                    lecture_best = lecture.getbest()
                    lecture_streams = lecture.streams
                    if caption_only and not skip_captions:
                        self.download_captions_only(lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                    elif skip_captions and not caption_only:
                        if quality:
                            index = 0
                            while index < len(lecture_streams):
                                dimension = int(lecture_streams[index].dimention[1])
                                if dimension == quality:
                                    lecture_best = lecture_streams[index]
                                    break
                                index += 1
                            if not lecture_best:
                                lecture_best = lecture_best
                        self.download_lectures_only(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=lecture_number, lectures_count=lectures_count, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                    else:
                        if quality:
                            index = 0
                            while index < len(lecture_streams):
                                dimension = int(lecture_streams[index].dimention[1])
                                if dimension == quality:
                                    lecture_best = lecture_streams[index]
                                    break
                                index += 1
                            if not lecture_best:
                                lecture_best = lecture_best
                        self.download_lectures_and_captions(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=lecture_number, lectures_count=lectures_count, lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                elif lecture_start and lecture_start > 0 and lecture_start <= lecture_end and lecture_end <= lectures_count:
                    while lecture_start <= lecture_end:
                        lecture = lectures[lecture_start-1]
                        lecture_id = lecture.id
                        lecture_index = lecture.index
                        lecture_title = lecture.title if not unsafe else "Lecture id : %s" % (lecture_id)
                        lecture_assets = lecture.assets
                        lecture_subtitles = lecture.subtitles
                        lecture_best = lecture.getbest()
                        lecture_streams = lecture.streams
                        if caption_only and not skip_captions:
                            self.download_captions_only(lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        elif skip_captions and not caption_only:
                            if quality:
                                index = 0
                                while index < len(lecture_streams):
                                    dimension = int(lecture_streams[index].dimention[1])
                                    if dimension == quality:
                                        lecture_best = lecture_streams[index]
                                        break
                                    index += 1
                                if not lecture_best:
                                    lecture_best = lecture_best
                            self.download_lectures_only(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=lecture_start, lectures_count=lecture_end, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        else:
                            if quality:
                                index = 0
                                while index < len(lecture_streams):
                                    dimension = int(lecture_streams[index].dimention[1])
                                    if dimension == quality:
                                        lecture_best = lecture_streams[index]
                                        break
                                    index += 1
                                if not lecture_best:
                                    lecture_best = lecture_best
                            self.download_lectures_and_captions(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=lecture_start, lectures_count=lecture_end, lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        lecture_start += 1
                else:
                    inner_index = 1
                    for lecture in lectures:
                        lecture_id = lecture.id
                        lecture_index = lecture.index
                        lecture_title = lecture.title if not unsafe else "Lecture id : %s" % (lecture_id)
                        lecture_assets = lecture.assets
                        lecture_subtitles = lecture.subtitles
                        lecture_best = lecture.getbest()
                        lecture_streams = lecture.streams
                        if caption_only and not skip_captions:
                            self.download_captions_only(lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        elif skip_captions and not caption_only:
                            if quality:
                                index = 0
                                while index < len(lecture_streams):
                                    dimension = int(lecture_streams[index].dimention[1])
                                    if dimension == quality:
                                        lecture_best = lecture_streams[index]
                                        break
                                    index += 1
                                if not lecture_best:
                                    lecture_best = lecture_best
                            self.download_lectures_only(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=inner_index, lectures_count=lectures_count, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        else:
                            if quality:
                                index = 0
                                while index < len(lecture_streams):
                                    dimension = int(lecture_streams[index].dimention[1])
                                    if dimension == quality:
                                        lecture_best = lecture_streams[index]
                                        break
                                    index += 1
                                if not lecture_best:
                                    lecture_best = lecture_best
                            self.download_lectures_and_captions(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=inner_index, lectures_count=lectures_count, lecture_subtitles=lecture_subtitles, language=language, lecture_assets=lecture_assets, filepath=filepath, unsafe=unsafe)
                        inner_index += 1
                chapter_start += 1
        else:
            if not chapter_end and not chapter_number and not chapter_start:
                sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Argument(s) are missing : Chapter(s) range or chapter(s) number is required.\n")
            elif chapter_end and chapter_end > total_chapters or chapter_number and chapter_number > total_chapters:
                sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Chapter(s) Range exceeded : Chapter(s) ending or chapter(s) number is out of range\n")
            elif chapter_start and chapter_start > chapter_end:
                sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Chapter(s) Range exception : Chapter(s) starting point cannot be greater than chapter(s) ending point\n")
            elif chapter_end and not chapter_start:
                sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Argument(s) are missing : Chapter(s) range starting point is missing ..\n")
            sys.stdout.write (fc + sd + "[" + fy + sb + "i" + fc + sd + "] : " + fw + sb + "Chapter(s) number or range should be in between ({start} to {end}).\n".format(start=1, end=total_chapters))
            sys.exit(0)

def main():
    sys.stdout.write(banner())
    version     = "%(prog)s {version}".format(version=__version__)
    description = 'A cross-platform python based utility to download courses from udemy for personal offline use.'
    parser = argparse.ArgumentParser(description=description, conflict_handler="resolve")
    parser.add_argument('course', help="Udemy course.", type=str)
    general = parser.add_argument_group("General")
    general.add_argument(
        '-h', '--help',\
        action='help',\
        help="Shows the help.")
    general.add_argument(
        '-v', '--version',\
        action='version',\
        version=version,\
        help="Shows the version.")

    authentication = parser.add_argument_group("Authentication")
    authentication.add_argument(
        '-u', '--username',\
        dest='username',\
        type=str,\
        help="Username in udemy.",metavar='')
    authentication.add_argument(
        '-p', '--password',\
        dest='password',\
        type=str,\
        help="Password of your account.",metavar='')
    authentication.add_argument(
        '-k', '--cookies',\
        dest='cookies',\
        type=str,\
        help="Cookies to authenticate with.",metavar='')

    advance = parser.add_argument_group("Advance")
    advance.add_argument(
        '-o', '--output',\
        dest='output',\
        type=str,\
        help="Download to specific directory.",metavar='')
    advance.add_argument(
        '-q', '--quality',\
        dest='quality',\
        type=int,\
        help="Download specific video quality.",metavar='')
    advance.add_argument(
        '-c', '--chapter',\
        dest='chapter',\
        type=int,\
        help="Download specific chapter from course.",metavar='')
    advance.add_argument(
        '-l', '--lecture',\
        dest='lecture',\
        type=int,\
        help="Download specific lecture from chapter(s).",metavar='')
    advance.add_argument(
        '-s', '--sub-lang',\
        dest='language',\
        type=str,\
        help="Download specific subtitle/caption (e.g:- en).",metavar='')
    advance.add_argument(
        '--chapter-start',\
        dest='chapter_start',\
        type=int,\
        help="Download from specific position within course.",metavar='')
    advance.add_argument(
        '--chapter-end',\
        dest='chapter_end',\
        type=int,\
        help="Download till specific position within course.",metavar='')
    advance.add_argument(
        '--lecture-start',\
        dest='lecture_start',\
        type=int,\
        help="Download from specific position within chapter(s).",metavar='')
    advance.add_argument(
        '--lecture-end',\
        dest='lecture_end',\
        type=int,\
        help="Download till specific position within chapter(s).",metavar='')

    other = parser.add_argument_group("Others")
    other.add_argument(
        '--save',\
        dest='save',\
        action='store_true',\
        help="Do not download but save links to a file.")
    other.add_argument(
        '--info',\
        dest='list',\
        action='store_true',\
        help="List all lectures with available resolution.")
    other.add_argument(
        '--cache',\
        dest='cache',\
        action='store_true',\
        help="Cache your credentials to use it later.")
    other.add_argument(
        '--names',\
        dest='names_only',\
        action='store_true',\
        help="Do not download but save lecture names to file.")
    other.add_argument(
        '--unsafe',\
        dest='unsafe',\
        action='store_true',\
        help="Download all course with unsafe names.")
    other.add_argument(
        '--sub-only',\
        dest='caption_only',\
        action='store_true',\
        help="Download captions/subtitle only.")
    other.add_argument(
        '--skip-sub',\
        dest='skip_captions',\
        action='store_true',\
        help="Download course but skip captions/subtitle.")

    options = parser.parse_args()
    if options.names_only:
        options.save = True

    if options.cookies:
        f_in = open(options.cookies)
        cookies = '\n'.join([line for line in (l.strip() for l in f_in) if line])
        f_in.close()
        if options.cache:
            cache_credentials(username="", password="", quality=options.quality, output=options.output, language=options.language)
        udemy = Udemy(url=options.course, cookies=cookies)
        if not options.cache:
            config = use_cached_credentials()
            if config and isinstance(config, dict):
                sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Loading configs..")
                options.quality = config.get('quality')
                options.output = config.get('output')
                options.language = config.get('language')
                time.sleep(1)
                sys.stdout.write ("\r" + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Loading configs.. (" + fc + sb + "done" + fg + sd + ")\n")
                sys.stdout.flush()
        if options.list and not options.save:
                try:
                    udemy.course_list_down(chapter_number=options.chapter, lecture_number=options.lecture, unsafe=options.unsafe)
                except KeyboardInterrupt as e:
                    sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                    sys.exit(0)
        elif not options.list and options.save:
            try:
                udemy.course_save(path=options.output, quality=options.quality, caption_only=options.caption_only, skip_captions=options.skip_captions, names_only=options.names_only, unsafe=options.unsafe)
            except KeyboardInterrupt as e:
                sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                sys.exit(0)
        elif not options.list and not options.save:

            if options.chapter and not options.chapter_end and not options.chapter_start:

                if options.lecture and not options.lecture_end and not options.lecture_start:


                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_number=options.chapter,lecture_number=options.lecture, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_number=options.chapter,lecture_number=options.lecture, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_number=options.chapter,lecture_number=options.lecture, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                elif options.lecture_start and options.lecture_end and not options.lecture:


                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                elif options.lecture_start and not options.lecture_end and not options.lecture:


                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                else:
                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_number=options.chapter, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_number=options.chapter, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_number=options.chapter, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

            elif options.chapter_start and options.chapter_end and not options.chapter:
                
                if options.lecture and not options.lecture_end and not options.lecture_start:


                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_number=options.lecture, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_number=options.lecture, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_number=options.lecture, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                elif options.lecture_start and options.lecture_end and not options.lecture:


                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                elif options.lecture_start and not options.lecture_end and not options.lecture:


                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)
                        
                else:
                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

            elif options.chapter_start and not options.chapter_end and not options.chapter:
                
                if options.lecture and not options.lecture_end and not options.lecture_start:


                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, lecture_number=options.lecture, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, lecture_number=options.lecture, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_start=options.chapter_start, lecture_number=options.lecture, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                elif options.lecture_start and options.lecture_end and not options.lecture:


                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                elif options.lecture_start and not options.lecture_end and not options.lecture:


                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                else:
                    if options.caption_only and not options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                    elif not options.caption_only and options.skip_captions:
                        udemy.chapter_download(chapter_start=options.chapter_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                    else:
                        udemy.chapter_download(chapter_start=options.chapter_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

            else:

                if options.caption_only and not options.skip_captions:

                    udemy.course_download(caption_only=options.caption_only, path=options.output, language=options.language, unsafe=options.unsafe)

                elif not options.caption_only and options.skip_captions:

                    udemy.course_download(skip_captions=options.skip_captions, path=options.output, quality=options.quality, unsafe=options.unsafe)

                else:

                    udemy.course_download(path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

    if not options.cookies:
        if not options.username and not options.password:
            username = fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Username : " + fg + sb
            password = fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Password : " + fc + sb
            config = use_cached_credentials()
            if config and isinstance(config, dict):
                sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Loading configs..")
                email = config.get('username')
                passwd = config.get('password')
                options.quality = config.get('quality')
                options.output = config.get('output')
                options.language = config.get('language')
                time.sleep(1)
                if email and passwd:
                    sys.stdout.write ("\r" + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Loading configs.. (" + fc + sb + "done" + fg + sd + ")\n")
                else:
                    sys.stdout.write ("\r" + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Loading configs.. (" + fr + sb + "failed" + fg + sd + ")\n")
                    email = getpass.getuser(prompt=username)
                    passwd = getpass.getpass(prompt=password)
                    print("")
            else:
                email = getpass.getuser(prompt=username)
                passwd = getpass.getpass(prompt=password)
                print("")
            if email and passwd:
                if options.cache:
                    cache_credentials(username=email, password=passwd, quality=options.quality, output=options.output, language=options.language)
                udemy = Udemy(url=options.course, username=email, password=passwd)
            else:
                sys.stdout.write('\n' + fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Username and password is required.\n")
                sys.exit(0)

            if options.list and not options.save:
                try:
                    udemy.course_list_down(chapter_number=options.chapter, lecture_number=options.lecture, unsafe=options.unsafe)
                except KeyboardInterrupt as e:
                    sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                    sys.exit(0)
            elif not options.list and options.save:
                try:
                    udemy.course_save(path=options.output, quality=options.quality, caption_only=options.caption_only, skip_captions=options.skip_captions, names_only=options.names_only, unsafe=options.unsafe)
                except KeyboardInterrupt as e:
                    sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                    sys.exit(0)
            elif not options.list and not options.save:

                if options.chapter and not options.chapter_end and not options.chapter_start:

                    if options.lecture and not options.lecture_end and not options.lecture_start:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter,lecture_number=options.lecture, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter,lecture_number=options.lecture, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_number=options.chapter,lecture_number=options.lecture, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and not options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    else:
                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_number=options.chapter, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                elif options.chapter_start and options.chapter_end and not options.chapter:
                    
                    if options.lecture and not options.lecture_end and not options.lecture_start:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_number=options.lecture, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_number=options.lecture, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_number=options.lecture, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and not options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)
                            
                    else:
                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                elif options.chapter_start and not options.chapter_end and not options.chapter:
                    
                    if options.lecture and not options.lecture_end and not options.lecture_start:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_number=options.lecture, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_number=options.lecture, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_number=options.lecture, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and not options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    else:
                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                else:

                    if options.caption_only and not options.skip_captions:

                        udemy.course_download(caption_only=options.caption_only, path=options.output, language=options.language, unsafe=options.unsafe)

                    elif not options.caption_only and options.skip_captions:

                        udemy.course_download(skip_captions=options.skip_captions, path=options.output, quality=options.quality, unsafe=options.unsafe)

                    else:

                        udemy.course_download(path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

        elif options.username and options.password:
            
            udemy = Udemy(url=options.course, username=options.username, password=options.password)
            
            if options.cache:
                cache_credentials(username=options.username, password=options.password, quality=options.quality, output=options.output, language=options.language)

            if options.list and not options.save:
                try:
                    udemy.course_list_down(chapter_number=options.chapter, lecture_number=options.lecture, unsafe=options.unsafe)
                except KeyboardInterrupt as e:
                    sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                    sys.exit(0)
            elif not options.list and options.save:
                # pprint(vars(options))
                # exit(0)
                try:
                    udemy.course_save(path=options.output, quality=options.quality, caption_only=options.caption_only, skip_captions=options.skip_captions, names_only=options.names_only, unsafe=options.unsafe)
                except KeyboardInterrupt as e:
                    sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                    sys.exit(0)
            elif not options.list and not options.save:

                if options.chapter and not options.chapter_end and not options.chapter_start:

                    if options.lecture and not options.lecture_end and not options.lecture_start:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter,lecture_number=options.lecture, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter,lecture_number=options.lecture, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_number=options.chapter,lecture_number=options.lecture, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and not options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_number=options.chapter, lecture_start=options.lecture_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    else:
                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_number=options.chapter, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_number=options.chapter, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                elif options.chapter_start and options.chapter_end and not options.chapter:

                    if options.lecture and not options.lecture_end and not options.lecture_start:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_number=options.lecture, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_number=options.lecture, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_number=options.lecture, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and not options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, lecture_start=options.lecture_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    else:
                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, chapter_end=options.chapter_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                elif options.chapter_start and not options.chapter_end and not options.chapter:

                    if options.lecture and not options.lecture_end and not options.lecture_start:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_number=options.lecture, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_number=options.lecture, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_number=options.lecture, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, lecture_end=options.lecture_end, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    elif options.lecture_start and not options.lecture_end and not options.lecture:


                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, lecture_start=options.lecture_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                    else:
                        if options.caption_only and not options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, path=options.output, language=options.language, caption_only=options.caption_only, unsafe=options.unsafe)
                        elif not options.caption_only and options.skip_captions:
                            udemy.chapter_download(chapter_start=options.chapter_start, path=options.output, quality=options.quality, skip_captions=options.skip_captions, unsafe=options.unsafe)
                        else:
                            udemy.chapter_download(chapter_start=options.chapter_start, path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

                else:

                    if options.caption_only and not options.skip_captions:

                        udemy.course_download(caption_only=options.caption_only, path=options.output, language=options.language, unsafe=options.unsafe)

                    elif not options.caption_only and options.skip_captions:

                        udemy.course_download(skip_captions=options.skip_captions, path=options.output, quality=options.quality, unsafe=options.unsafe)

                    else:

                        udemy.course_download(path=options.output, language=options.language, quality=options.quality, unsafe=options.unsafe)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
        sys.exit(0)
