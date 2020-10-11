# pylint: disable=R,C,W
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Author  : Nasir Khan (r0ot h3x49)
Github  : https://github.com/r0oth3x49
License : MIT


Copyright (c) 2018-2025 Nasir Khan (r0ot h3x49)

Permission is hereby granted, Fore.REDee of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modiFore.YELLOW, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFore.REDINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING Fore.REDOM, OUT OF OR IN CONNECTION WITH 
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys
import logging
from udemy.compat import os, re
from colorama import init, Fore, Style
from udemy.progress import ProgressBar

init(autoreset=True)
log = logging.getLogger("udemy-dl")  # pylint: disable=C


def set_color(string, level=None):
    """
    set the string color
    """
    color_levels = {
        10: "%s%s{}" % (Style.BRIGHT, Fore.YELLOW),
        15: "%s%s{}" % (Style.BRIGHT, Fore.WHITE),
        20: "%s%s{}" % (Style.DIM, Fore.GREEN),
        30: "%s%s{}" % (Style.BRIGHT, Fore.CYAN),
        40: "%s%s{}" % (Style.BRIGHT, Fore.RED),
        50: "%s%s{}" % (Style.DIM, Fore.BLUE),
        55: "%s%s{}" % (Style.BRIGHT, Fore.BLUE),
        60: "%s%s{}" % (Style.DIM, Fore.WHITE),
        70: "%s%s{}" % (Style.BRIGHT, Fore.GREEN),
        80: "%s%s{}" % (Style.BRIGHT, Fore.MAGENTA),
        90: "%s%s{}" % (Style.DIM, Fore.MAGENTA),
    }
    if level is None:
        return color_levels[70].format(string)
    else:
        return color_levels[int(level)].format(string)


class Logging(ProgressBar):
    """
        Custom logging class for udemy
    """

    def __init__(self):
        self._log_filepath = None

    def set_log_filepath(self, course_path):
        course_path = re.sub(r'"', "", course_path.strip())
        if os.path.exists(course_path):
            self._log_filepath = os.path.join(course_path, "udemy-dl.log")
            file_handler = logging.FileHandler(self._log_filepath)
            logging.basicConfig(
                format="[%(asctime)s][%(name)s] %(levelname)-5.5s %(message)s",
                level=logging.INFO,
                handlers=[file_handler],
            )

    def info(
        self,
        msg,
        status="",
        new_line=False,
        before=False,
        indent=None,
        cc=None,
        cc_msg=None,
        post_msg=None,
        cc_pmsg=None,
    ):
        """This function prints already downloaded msg"""
        _type = set_color(string="i", level=cc if cc else 80)
        prefix = (
            "\033[2K\033[1G\r\r"
            + Fore.CYAN
            + Style.DIM
            + "["
            + _type
            + Fore.CYAN
            + Style.DIM
            + "] : "
        )
        if indent:
            prefix = set_color(
                string=f"\033[2K\033[1G\r\r{indent}", level=cc if cc else 30
            )
        if status:
            # log.info(f"{msg} ({status})")
            msg = (
                set_color(f"{msg} (", level=cc_msg if cc_msg else 70)
                + set_color(status, level=80)
                + set_color(")\r\n", level=70)
            )
            string = prefix + msg
            sys.stdout.write(string)
            sys.stdout.flush()
        else:
            if not new_line:
                # log.info(f"{msg}")
                msg = set_color(f"{msg}\r", level=cc_msg if cc_msg else 70)
                string = prefix + msg
                sys.stdout.write(string)
                sys.stdout.flush()
            if new_line:
                if post_msg and cc_pmsg:
                    # log.info(f"{msg}{post_msg}")
                    msg = set_color(f"{msg}", level=cc_msg if cc_msg else 70)
                    post_msg = set_color(string=f"{post_msg}\r\n", level=cc_pmsg)
                    msg += post_msg
                else:
                    # log.info(f"{msg}")
                    msg = set_color(f"{msg}\r\n", level=cc_msg if cc_msg else 70)
                string = prefix + msg
                if before:
                    string = "\r\n" + string
                sys.stdout.write(string)
                sys.stdout.flush()

    def progress(self, msg):
        prefix = (
            "\033[2K\033[1G\r\r"
            + Fore.CYAN
            + Style.DIM
            + "["
            + Fore.MAGENTA
            + Style.BRIGHT
            + "i"
            + Fore.CYAN
            + Style.DIM
            + "] : "
        )
        msg = set_color(f"{msg}", level=70)
        string = prefix + msg
        self._spinner(string)

    def success(self, msg, course=False):
        """This function prints already downloaded msg"""
        prefix = (
            "\033[2K\033[1G\r\r"
            + Fore.CYAN
            + Style.DIM
            + "["
            + Fore.MAGENTA
            + Style.BRIGHT
            + "+"
            + Fore.CYAN
            + Style.DIM
            + "] : "
        )
        if course:
            msg = set_color("Course ", level=70) + set_color(f"'{msg}'\r\n", level=55)
            string = prefix + msg
            sys.stdout.write(string)
            sys.stdout.flush()
        if not course:
            msg = (
                set_color(f"{msg} (", level=70)
                + set_color("done", level=30)
                + set_color(")\r\n", level=70)
            )
            string = prefix + msg
            sys.stdout.write(string)
            sys.stdout.flush()

    def failed(self, msg):
        """This function prints already downloaded msg"""
        prefix = (
            "\033[2K\033[1G\r\r"
            + Fore.CYAN
            + Style.DIM
            + "["
            + Fore.RED
            + Style.BRIGHT
            + "-"
            + Fore.CYAN
            + Style.DIM
            + "] : "
        )
        if self._log_filepath:
            log.error(f"{msg} (failed)")
        msg = (
            set_color(f"{msg} (", level=70)
            + set_color("failed", level=40)
            + set_color(")\r\n", level=70)
        )
        string = prefix + msg
        sys.stdout.write(string)
        sys.stdout.flush()

    def warning(self, msg, silent=False):
        """This function prints already downloaded msg"""
        prefix = (
            "\033[2K\033[1G\r\r"
            + Fore.CYAN
            + Style.DIM
            + "["
            + Fore.MAGENTA
            + Style.BRIGHT
            + "*"
            + Fore.CYAN
            + Style.DIM
            + "] : "
        )
        if self._log_filepath:
            log.warning(msg)
        msg = set_color(f"{msg}\n", level=10)
        string = prefix + msg
        if not silent:
            sys.stdout.write(string)
            sys.stdout.flush()

    def error(self, msg, new_line=False):
        """This function prints already downloaded msg"""
        prefix = (
            "\033[2K\033[1G\r\r"
            + Fore.CYAN
            + Style.DIM
            + "["
            + Fore.RED
            + Style.BRIGHT
            + "-"
            + Fore.CYAN
            + Style.DIM
            + "] : "
        )
        if self._log_filepath:
            log.error(msg)
        if not new_line:
            msg = set_color(f"{msg}\n", level=40)
            string = prefix + msg
            sys.stdout.write(string)
            sys.stdout.flush()
        if new_line:
            msg = set_color(f"{msg}\n", level=40)
            string = "\n" + prefix + msg
            sys.stdout.write(string)
            sys.stdout.flush()

    def already_downloaded(self, msg):
        """This function prints already downloaded msg"""
        prefix = (
            "\033[2K\033[1G\r\r"
            + Fore.CYAN
            + Style.DIM
            + "["
            + Fore.MAGENTA
            + Style.BRIGHT
            + "+"
            + Fore.CYAN
            + Style.DIM
            + "] : "
        )
        msg = (
            set_color(f"{msg} (", level=70)
            + set_color("already downloaded", level=10)
            + set_color(")\r\n", level=70)
        )
        string = prefix + msg
        sys.stdout.write(string)
        sys.stdout.flush()

    def download_skipped(self, msg, reason=""):
        """This function prints already downloaded msg"""
        prefix = (
            "\033[2K\033[1G\r\r"
            + Fore.CYAN
            + Style.DIM
            + "["
            + Fore.MAGENTA
            + Style.BRIGHT
            + "+"
            + Fore.CYAN
            + Style.DIM
            + "] : "
        )
        if self._log_filepath:
            log.warning(f"{msg} (download skipped)")
        msg = (
            set_color(f"{msg} (", level=70)
            + set_color("download skipped", level=30)
            + set_color(")\r\n", level=70)
        )
        string = prefix + msg
        sys.stdout.write(string)
        sys.stdout.flush()
        if reason:
            self.error(msg=reason, new_line=True)


logger = Logging()
