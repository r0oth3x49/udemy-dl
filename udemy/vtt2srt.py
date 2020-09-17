# pylint: disable=R,C
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
from udemy.utils import unescapeHTML
from udemy.compat import os, re  # , codecs


class WebVtt2Srt(object):

    _TIMECODE_REGEX = r"(?i)(?P<appeartime>(?:(?:\d{1,2}:)){1,2}\d{2}[\.,]\d+)"
    _TIMECODE = r"(?i)(?P<appeartime>(?:(?:\d{1,2}:)){1,2}\d{2}[\.,]\d+)\s*-->\s*(?i)(?P<disappertime>(?:(?:\d{1,2}:)){1,2}\d{2}[\.,]\d+)"

    def _vttcontents(self, fname):
        content = []
        try:
            # f = codecs.open(filename=fname, encoding="utf-8", errors="ignore")
            with open(fname, encoding="utf-8", errors="ignore") as f:
                content = [line for line in (l.strip() for l in f)]
        except Exception as error:  # pylint: disable=W
            return {
                "status": "False",
                "msg": f"failed to open file : error: {error} ..",
            }
        # content = [line for line in (l.strip() for l in f)]
        # f.close()
        return content

    def _write_srtcontent(self, fname, content):
        with open(fname, mode="a", encoding="utf-8", errors="ignore") as fd:
            fd.write(content)
        # fd.close()

    def _locate_timecode(self, content):
        loc = ""
        for (loc, line) in enumerate(content):
            match = re.match(self._TIMECODE_REGEX, line, flags=re.U)
            if match:
                return {"status": True, "location": loc}
        return {"status": False, "location": loc}

    def _is_timecode(self, timecode):
        match = re.match(self._TIMECODE_REGEX, timecode, flags=re.U)
        if match:
            return True
        return False

    def _fix_timecode(self, timecode):
        _sdata = len(timecode.split(",")[0])
        if _sdata == 5:
            timecode = "00:{code}".format(code=timecode)
        if _sdata == 7:
            timecode = "0{code}".format(code=timecode)
        return timecode

    def _generate_timecode(self, sequence, timecode):
        match = re.match(self._TIMECODE, timecode, flags=re.U)
        if match:
            start, end = (
                self._fix_timecode(
                    timecode=re.sub(r"[\.,]", ",", match.group("appeartime"))
                ),
                self._fix_timecode(
                    timecode=re.sub(r"[\.,]", ",", match.group("disappertime"))
                ),
            )
            return "{seq}\r\n{appeartime} --> {disappertime}\r\n".format(
                seq=sequence, appeartime=start, disappertime=end
            )
        return ""

    def convert(self, filename=None, keep_vtt=False):
        if filename:
            seq = 1
            fname = filename.replace(".vtt", ".srt")
            content = self._vttcontents(fname=filename)
            if content and isinstance(content, list):
                timecode_loc = self._locate_timecode(content)
                if not timecode_loc.get("status"):
                    return {
                        "status": "False",
                        "msg": "subtitle file seems to have malfunction skipping conversion ..",
                    }
                for line in content[timecode_loc.get("location") :]:
                    flag = self._is_timecode(timecode=line)
                    if flag:
                        timecode = self._generate_timecode(seq, unescapeHTML(line))
                        self._write_srtcontent(fname, timecode)
                        seq += 1
                    if not flag:
                        match = re.match("^([0-9]{1,3})$", line, flags=re.U)
                        if not match:
                            data = "{content}\r\n".format(content=line)
                            self._write_srtcontent(fname, data)
            else:
                return content

            if not keep_vtt:
                try:
                    os.unlink(filename)
                except Exception:  # pylint: disable=W
                    pass
        return {"status": "True", "msg": "successfully generated subtitle in srt ..."}
