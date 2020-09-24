#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=R,C0330,C0301,C0303

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

import os
import sys
import argparse

import udemy
from udemy.logger import logger
from udemy.getpass import getpass
from udemy.vtt2srt import WebVtt2Srt
from udemy.progress import ProgressBar
from udemy.colorized.banner import banner
from udemy.utils import (
    to_configs,
    to_filepath,
    load_configs,
    to_human_readable,
    extract_url_or_courses,
)


class Udemy(WebVtt2Srt, ProgressBar):
    """Udemy is class which implements downloading/lising and all"""

    def __init__(self, url_or_courses, username="", password="", cookies=""):
        self.username = username
        self.password = password
        self.cookies = cookies
        self.url_or_courses = url_or_courses
        super(Udemy, self).__init__()

    def download_assets(self, assets, filepath):
        """This function will simply download the asstes.."""
        if assets:
            for asset in assets:
                title = asset.filename
                logger.info(msg="Downloading asset(s)", new_line=True, before=True)
                logger.info(msg=f"Downloading ({title})", new_line=True)
                try:
                    retval = asset.download(
                        filepath=filepath, quiet=True, callback=self.show_progress,
                    )
                    msg = retval.get("msg")
                    if msg == "already downloaded":
                        logger.already_downloaded(msg=f"Asset : '{title}'")
                    elif msg == "download":
                        logger.info(msg=f"Downloaded  ({title})", new_line=True)
                    else:
                        logger.download_skipped(msg=f"Asset : '{title}' ", reason=msg)
                except KeyboardInterrupt:
                    logger.error(msg="User Interrupted..", new_line=True)
                    sys.exit(0)

    def download_lecture(self, lecture, filepath, current, total, quality):
        """This function will simply download the lectures.."""
        if quality and lecture:
            lecture = lecture.get_quality(quality)
        if lecture:
            title = lecture.title
            logger.info(
                msg=f"Lecture(s) : ({current} of {total})", new_line=True, before=True
            )
            logger.info(msg=f"Downloading ({title})", new_line=True)
            try:
                retval = lecture.download(
                    filepath=filepath, quiet=True, callback=self.show_progress,
                )
                msg = retval.get("msg")
                if msg == "already downloaded":
                    logger.already_downloaded(msg=f"Lecture : '{title}'")
                elif msg == "download":
                    logger.info(msg=f"Downloaded  ({title})", new_line=True)
                else:
                    logger.download_skipped(msg=f"Lecture : '{title}' ", reason=msg)
            except KeyboardInterrupt:
                logger.error(msg="User Interrupted..", new_line=True)
                sys.exit(0)

    def download_subtitles(self, subtitles, filepath, language="en", keep_vtt=False):
        """This function will simply download the subtitles.."""
        if language and subtitles:
            subtitle = subtitles.pop()
            subtitles = subtitle.get_subtitle(language)
        if subtitles:
            for sub in subtitles:
                title = f"{sub.title}.{sub.language}"
                filename = os.path.join(filepath, sub.filename)
                logger.info(msg="Downloading subtitle(s)", new_line=True, before=True)
                logger.info(msg=f"Downloading ({title})", new_line=True)
                try:
                    retval = sub.download(
                        filepath=filepath, quiet=True, callback=self.show_progress,
                    )
                    msg = retval.get("msg")
                    if msg == "already downloaded":
                        logger.already_downloaded(msg=f"Subtitle : '{title}'")
                    elif msg == "download":
                        logger.info(msg=f"Downloaded  ({title})", new_line=True)
                        self.convert(filename=filename, keep_vtt=keep_vtt)
                    else:
                        logger.download_skipped(
                            msg=f"Subtitle : '{title}' ", reason=msg
                        )
                except KeyboardInterrupt:
                    logger.error(msg="User Interrupted..", new_line=True)
                    sys.exit(0)

    def course_listdown(
        self,
        chapter_number=None,
        chapter_start=None,
        chapter_end=None,
        lecture_number=None,
        lecture_start=None,
        lecture_end=None,
        skip_hls_stream=False,
    ):
        """This function will listdown the course contents .."""
        if not self.cookies:
            logger.info(msg="Trying to login as", status=self.username)
        if self.cookies:
            logger.info(msg="Trying to login using session cookie", new_line=True)
        for url in self.url_or_courses:
            course = udemy.course(
                url=url,
                username=self.username,
                password=self.password,
                cookies=self.cookies,
                skip_hls_stream=skip_hls_stream,
            )
            course_name = course.title
            chapters = course.get_chapters(
                chapter_number=chapter_number,
                chapter_start=chapter_start,
                chapter_end=chapter_end,
            )
            total_lectures = course.lectures
            total_chapters = course.chapters
            logger.success(msg=course_name, course=True)
            logger.info(msg=f"Chapter(s) ({total_chapters})", new_line=True)
            logger.info(msg=f"Lecture(s) ({total_lectures})", new_line=True)
            for chapter in chapters:
                chapter_id = chapter.id
                chapter_title = chapter.title
                lectures = chapter.get_lectures(
                    lecture_number=lecture_number,
                    lecture_start=lecture_start,
                    lecture_end=lecture_end,
                )
                lectures_count = chapter.lectures
                logger.info(
                    msg=f"Chapter ({chapter_title}-{chapter_id})",
                    new_line=True,
                    before=True,
                    cc=15,
                    cc_msg=15,
                )
                logger.info(msg=f"Lecture(s) ({lectures_count})", new_line=True)
                for lecture in lectures:
                    lecture_id = lecture.id
                    lecture_streams = lecture.streams
                    lecture_best = lecture.getbest()
                    lecture_assets = lecture.assets
                    lecture_subtitles = lecture.subtitles
                    if not lecture_streams:
                        continue
                    logger.info(
                        indent="     - ",
                        msg="duration   : ",
                        new_line=True,
                        cc=80,
                        cc_msg=10,
                        post_msg=f"{lecture.duration}.",
                        cc_pmsg=80,
                    )
                    logger.info(
                        indent="     - ",
                        msg="Lecture id : ",
                        new_line=True,
                        cc=80,
                        cc_msg=10,
                        post_msg=f"{lecture_id}.",
                        cc_pmsg=80,
                    )
                    indent = "\t- "
                    for stream in lecture_streams:
                        post_msg = None
                        if stream.is_hls:
                            human_readable = ""
                        if not stream.is_hls:
                            content_length = stream.get_filesize()
                            if content_length == 0:
                                continue
                            human_readable = to_human_readable(content_length)
                            if lecture_best.quality == stream.quality:
                                post_msg = "(Best)"
                        msg = "{:<22} {:<8}{}".format(
                            f"{stream}", f"{stream.quality}p", human_readable
                        )
                        logger.info(
                            indent=indent,
                            msg=msg,
                            new_line=True,
                            cc=15,
                            post_msg=post_msg,
                            cc_pmsg=30,
                        )
                    if lecture_assets:
                        for asset in lecture_assets:
                            if asset.mediatype == "external_link":
                                continue
                            content_length = asset.get_filesize()
                            if content_length == 0:
                                continue
                            human_readable = to_human_readable(content_length)
                            msg = "{:<22} {:<8}{}".format(
                                f"{asset}", asset.extension, human_readable
                            )
                            logger.info(
                                indent=indent, msg=msg, new_line=True, cc=15,
                            )
                    if lecture_subtitles:
                        for sub in lecture_subtitles:
                            content_length = sub.get_filesize()
                            if content_length == 0:
                                continue
                            human_readable = to_human_readable(content_length)
                            msg = "{:<22} {:<8}{}".format(
                                f"{sub}", sub.extension, human_readable
                            )
                            logger.info(
                                indent=indent, msg=msg, new_line=True, cc=15,
                            )
            print("")

    def course_download(
        self,
        path="",
        quality="",
        language="en",
        dl_assets=True,
        dl_lecture=True,
        dl_subtitles=True,
        chapter_number=None,
        chapter_start=None,
        chapter_end=None,
        lecture_number=None,
        lecture_start=None,
        lecture_end=None,
        keep_vtt=False,
        skip_hls_stream=False,
    ):
        """This function will download the course contents .."""
        if not self.cookies:
            logger.info(msg="Trying to login as", status=self.username)
        if self.cookies:
            logger.info(msg="Trying to login using session cookie", new_line=True)
        for url in self.url_or_courses:
            course = udemy.course(
                url=url,
                username=self.username,
                password=self.password,
                cookies=self.cookies,
                skip_hls_stream=skip_hls_stream,
            )
            course_name = course.title
            if path:
                if "~" in path:
                    path = os.path.expanduser(path)
            course_path = os.path.join(path, course_name)
            chapters = course.get_chapters(
                chapter_number=chapter_number,
                chapter_start=chapter_start,
                chapter_end=chapter_end,
            )
            total_lectures = course.lectures
            total_chapters = course.chapters
            logger.success(msg=course_name, course=True)
            logger.info(msg=f"Chapter(s) ({total_chapters})", new_line=True)
            logger.info(msg=f"Lecture(s) ({total_lectures})", new_line=True)
            for chapter in chapters:
                chapter_index = chapter.index
                chapter_title = chapter.title
                lectures = chapter.get_lectures(
                    lecture_number=lecture_number,
                    lecture_start=lecture_start,
                    lecture_end=lecture_end,
                )
                lectures_count = chapter.lectures
                filepath = to_filepath(course_path, chapter_title)
                logger.set_log_filepath(course_path)
                chapter_progress = (
                    chapter_index
                    if chapter_number
                    else f"{chapter_index} of {total_chapters}"
                )
                logger.info(
                    msg=f"Downloading chapter : ({chapter_progress})",
                    new_line=True,
                    before=True,
                    cc=80,
                    cc_msg=80,
                )
                logger.info(
                    msg=f"Chapter ({chapter_title})", new_line=True, cc=15, cc_msg=60
                )
                logger.info(
                    msg=f"Found ({lectures_count}) lecture(s).", new_line=True,
                )
                lecture_index = 0
                if lecture_number:
                    lecture_index = lecture_number - 1
                if lecture_start:
                    lecture_index = lecture_start - 1
                if lecture_index < 0:
                    lecture_index = 0
                for lecture in lectures:
                    lecture_assets = lecture.assets
                    lecture_subtitles = lecture.subtitles
                    lecture_best = lecture.getbest()
                    if dl_lecture:
                        lecture_index = lecture_index + 1
                        if lecture.html:
                            retval = lecture.dump(filepath=filepath)
                            msg = retval.get("msg")
                            if msg not in ["download", "already downloaded"]:
                                msg = f"Lecture: '{lecture.title}.{lecture.extension}' failed to dump, reason: {msg}"
                                logger.warning(msg=msg, silent=True)
                        self.download_lecture(
                            lecture_best,
                            filepath,
                            lecture_index,
                            lectures_count,
                            quality,
                        )
                    if dl_assets:
                        self.download_assets(lecture_assets, filepath)
                    if dl_subtitles:
                        self.download_subtitles(
                            lecture_subtitles,
                            filepath,
                            language=language,
                            keep_vtt=keep_vtt,
                        )
            print("")


def main():
    """main function"""
    sys.stdout.write(banner())
    version = "%(prog)s {version}".format(version="1.0")
    description = "A cross-platform python based utility to download courses from udemy for personal offline use."
    parser = argparse.ArgumentParser(
        description=description, conflict_handler="resolve"
    )
    parser.add_argument("course", help="Udemy course.", type=str)
    general = parser.add_argument_group("General")
    general.add_argument("-h", "--help", action="help", help="Shows the help.")
    general.add_argument(
        "-v", "--version", action="version", version=version, help="Shows the version."
    )

    authentication = parser.add_argument_group("Authentication")
    authentication.add_argument(
        "-u",
        "--username",
        dest="username",
        type=str,
        help="Username in udemy.",
        metavar="",
    )
    authentication.add_argument(
        "-p",
        "--password",
        dest="password",
        type=str,
        help="Password of your account.",
        metavar="",
    )
    authentication.add_argument(
        "-k",
        "--cookies",
        dest="cookies",
        type=str,
        help="Cookies to authenticate with.",
        metavar="",
    )

    advance = parser.add_argument_group("Advance")
    advance.add_argument(
        "-o",
        "--output",
        dest="output",
        type=str,
        default=os.getcwd(),
        help="Download to specific directory.",
        metavar="",
    )
    advance.add_argument(
        "-q",
        "--quality",
        dest="quality",
        type=int,
        help="Download specific video quality.",
        metavar="",
    )
    advance.add_argument(
        "-c",
        "--chapter",
        dest="chapter",
        type=int,
        help="Download specific chapter from course.",
        metavar="",
    )
    advance.add_argument(
        "-l",
        "--lecture",
        dest="lecture",
        type=int,
        help="Download specific lecture from chapter(s).",
        metavar="",
    )
    advance.add_argument(
        "-s",
        "--sub-lang",
        dest="language",
        type=str,
        help="Download specific subtitle/caption (e.g:- en).",
        metavar="",
        default="en",
    )
    advance.add_argument(
        "--chapter-start",
        dest="chapter_start",
        type=int,
        help="Download from specific position within course.",
        metavar="",
    )
    advance.add_argument(
        "--chapter-end",
        dest="chapter_end",
        type=int,
        help="Download till specific position within course.",
        metavar="",
    )
    advance.add_argument(
        "--lecture-start",
        dest="lecture_start",
        type=int,
        help="Download from specific position within chapter(s).",
        metavar="",
    )
    advance.add_argument(
        "--lecture-end",
        dest="lecture_end",
        type=int,
        help="Download till specific position within chapter(s).",
        metavar="",
    )

    other = parser.add_argument_group("Others")
    other.add_argument(
        "--info",
        dest="info",
        action="store_true",
        help="List all lectures with available resolution.",
    )
    other.add_argument(
        "--keep-vtt",
        dest="keep_vtt",
        action="store_true",
        help="Keep WebVTT caption(s).",
    )
    other.add_argument(
        "--sub-only",
        dest="caption_only",
        action="store_true",
        help="Download captions/subtitle only.",
    )
    other.add_argument(
        "--skip-sub",
        dest="skip_captions",
        action="store_true",
        help="Download course but skip captions/subtitle.",
    )
    other.add_argument(
        "--skip-hls",
        dest="skip_hls_stream",
        action="store_true",
        help="Download course but skip hls streams. (fast fetching).",
    )
    other.add_argument(
        "--assets-only",
        dest="assets_only",
        action="store_true",
        help="Download asset(s) only.",
    )
    other.add_argument(
        "--skip-assets",
        dest="skip_assets",
        action="store_true",
        help="Download course but skip asset(s).",
    )

    args = parser.parse_args()
    if args.cookies:
        f_in = open(args.cookies)
        with open(args.cookies) as f_in:
            cookies = "\n".join([line for line in (l.strip() for l in f_in) if line])
        args.cookies = cookies
    if not args.username and not args.password and not args.cookies:
        configs = load_configs()
        if not configs:
            args.username = getpass.getuser(prompt="Username : ")
            args.password = getpass.getpass(prompt="Password : ")
            print("\n")
        if configs:
            cookies = configs.get("cookies")
            if not cookies:
                args.username = configs.get("username")
                args.password = configs.get("password")
            if cookies:
                args.cookies = cookies
            args.quality = args.quality if args.quality else configs.get("quality")
            args.output = args.output if args.output else configs.get("output")
            args.language = args.language if args.language else configs.get("language")
    url_or_courses = extract_url_or_courses(args.course)
    udemy_obj = Udemy(
        url_or_courses=url_or_courses,
        username=args.username,
        password=args.password,
        cookies=args.cookies,
    )
    # setting the caching default so that we can avoid future login attemps.
    _ = to_configs(
        username=args.username,
        password=args.password,
        cookies=args.cookies,
        quality=args.quality,
        output=args.output,
        language=args.language,
    )
    dl_assets = dl_lecture = dl_subtitles = True
    if args.assets_only:
        dl_lecture = False
        dl_subtitles = False
        args.skip_hls_stream = True
    if args.skip_assets:
        dl_assets = False
    if args.caption_only:
        dl_lecture = False
        dl_assets = False
        args.skip_hls_stream = True
    if args.skip_captions:
        dl_subtitles = False
    if not args.info:
        udemy_obj.course_download(
            path=args.output,
            quality=args.quality,
            language=args.language,
            dl_assets=dl_assets,
            dl_lecture=dl_lecture,
            dl_subtitles=dl_subtitles,
            chapter_number=args.chapter,
            chapter_start=args.chapter_start,
            chapter_end=args.chapter_end,
            lecture_number=args.lecture,
            lecture_start=args.lecture_start,
            lecture_end=args.lecture_end,
            keep_vtt=args.keep_vtt,
            skip_hls_stream=args.skip_hls_stream,
        )
    if args.info:
        udemy_obj.course_listdown(
            chapter_number=args.chapter,
            chapter_start=args.chapter_start,
            chapter_end=args.chapter_end,
            lecture_number=args.lecture,
            lecture_start=args.lecture_start,
            lecture_end=args.lecture_end,
            skip_hls_stream=args.skip_hls_stream,
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.error(msg="User Interrupted..", new_line=True)
        sys.exit(0)
