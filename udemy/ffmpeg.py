#!/usr/bin/python3
# pylint: disable=R,C,W,E

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
import subprocess
from udemy.compat import re, time

# from udemy.logger import logger
from udemy.progress import progress


class FFMPeg:

    _PROGRESS_PATTERN = re.compile(
        r"(frame|fps|total_size|out_time|bitrate|speed|progress)\s*\=\s*(\S+)"
    )

    def __init__(
        self, duration, url, token, filepath, quiet=False, callback=lambda *x: None
    ):
        self.url = url
        self.filepath = filepath
        self.quiet = quiet
        self.duration = duration
        self.callback = callback
        self.token = token

    def _command(self):
        """
        ffmpeg.exe -headers "Authorization: Bearer {token}" -i "" -c copy -bsf:a aac_adtstoasc out.mp4
        """
        command = [
            "ffmpeg",
            "-headers",
            f"Authorization: Bearer {self.token}",
            "-i",
            f"{self.url}",
            "-c",
            "copy",
            "-bsf:a",
            "aac_adtstoasc",
            f"{self.filepath}",
            "-y",
            "-progress",
            "pipe:2",
        ]
        return command

    def _fetch_total_duration(self, line):
        duration_in_secs = 0
        duration_regex = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2})\.\d{2}")
        mobj = duration_regex.search(line)
        if mobj:
            duration_tuple = mobj.groups()
            duration_in_secs = (
                int(duration_tuple[0]) * 60
                + int(duration_tuple[1]) * 60
                + int(duration_tuple[2])
            )
        else:
            duration_in_secs = self.duration
        return duration_in_secs

    def _fetch_current_duration_done(self, time_str):
        time_str = time_str.split(":")
        return (
            int(time_str[0]) * 60
            + int(time_str[1]) * 60
            + int(time_str[2].split(".")[0])
        )

    def _prepare_time_str(self, secs):
        (mins, secs) = divmod(secs, 60)
        (hours, mins) = divmod(mins, 60)
        if hours > 99:
            time_str = "--:--:--"
        if hours == 0:
            time_str = "%02d:%02ds" % (mins, secs)
        else:
            time_str = "%02d:%02d:%02ds" % (hours, mins, secs)
        return time_str

    def _progress(
        self, iterations, total, bytesdone, speed, elapsed, bar_length=30, fps=None
    ):
        offset = 0
        filled_length = int(round(bar_length * iterations / float(total)))
        percents = format(100.00 * (iterations * 1.0 / float(total)), ".2f")

        if bytesdone <= 1048576:
            _receiving = round(float(bytesdone) / 1024.00, 2)
            _received = format(
                _receiving if _receiving < 1024.00 else _receiving / 1024.00, ".2f"
            )
            suffix_recvd = "KB" if _receiving < 1024.00 else "MB"
        else:
            _receiving = round(float(bytesdone) / 1048576, 2)
            _received = format(
                _receiving if _receiving < 1024.00 else _receiving / 1024.00, ".2f"
            )
            suffix_recvd = "MB" if _receiving < 1024.00 else "GB"

        suffix_rate = "Kb/s" if speed < 1024.00 else "Mb/s"
        if fps:
            suffix_rate += f" {fps}/fps"
        if elapsed:
            rate = ((float(iterations) - float(offset)) / 1024.0) / elapsed
            eta = (total - iterations) / (rate * 1024.0)
        else:
            rate = 0
            eta = 0
        rate = format(speed if speed < 1024.00 else speed / 1024.00, ".2f")
        (mins, secs) = divmod(eta, 60)
        (hours, mins) = divmod(mins, 60)
        if hours > 99:
            eta = "--:--:--"
        if hours == 0:
            eta = "eta %02d:%02ds" % (mins, secs)
        else:
            eta = "eta %02d:%02d:%02ds" % (hours, mins, secs)
        if secs == 0:
            eta = "\n"

        total_time = self._prepare_time_str(total)
        done_time = self._prepare_time_str(iterations)
        downloaded = f"{total_time}/{done_time}"

        received_bytes = str(_received) + str(suffix_recvd)
        percents = f"{received_bytes} {percents}"

        progress.hls_progress(
            downloaded=downloaded,
            percents=percents,
            filled_length=filled_length,
            rate=str(rate) + str(suffix_rate),
            suffix=eta,
            bar_length=bar_length,
        )

    def _parse_progress(self, line):
        items = {key: value for key, value in self._PROGRESS_PATTERN.findall(line)}
        return items

    def download(self):
        total_time = None
        t0 = time.time()
        progress_lines = []
        active = True
        retVal = {}
        command = self._command()
        bytes_done = 0
        download_speed = 0
        try:
            with subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as proc:
                while active:
                    elapsed = time.time() - t0
                    try:
                        line = proc.stderr.readline().decode("utf-8").strip()
                        if not total_time:
                            total_time = self._fetch_total_duration(line)
                        if "progress=end" in line:
                            try:
                                self._progress(
                                    total_time,
                                    total_time,
                                    bytes_done,
                                    download_speed,
                                    elapsed,
                                )
                            except KeyboardInterrupt:
                                retVal = {
                                    "status": "False",
                                    "msg": "Error: KeyboardInterrupt",
                                }
                                raise KeyboardInterrupt
                            except Exception as err:
                                {"status": "False", "msg": f"Error: {err}"}
                            active = False
                            retVal = {"status": "True", "msg": "download"}
                            break
                        if "progress" not in line:
                            progress_lines.append(line)
                        else:
                            lines = "\n".join(progress_lines)
                            items = self._parse_progress(lines)
                            if items:
                                secs = self._fetch_current_duration_done(
                                    items.get("out_time")
                                )
                                _tsize = (
                                    items.get("total_size").lower().replace("kb", "")
                                )
                                _brate = (
                                    items.get("bitrate").lower().replace("kbits/s", "")
                                )
                                fps = items.get("fps")
                                bytes_done = float(_tsize) if _tsize != "n/a" else 0
                                download_speed = float(_brate) if _brate != "n/a" else 0
                                try:
                                    self._progress(
                                        secs,
                                        total_time,
                                        bytes_done,
                                        download_speed,
                                        elapsed,
                                        fps=fps,
                                    )
                                except KeyboardInterrupt:
                                    retVal = {
                                        "status": "False",
                                        "msg": "Error: KeyboardInterrupt",
                                    }
                                    raise KeyboardInterrupt
                                except Exception as err:
                                    {"status": "False", "msg": f"Error: {err}"}
                            progress_lines = []
                    except KeyboardInterrupt:
                        active = False
                        retVal = {"status": "False", "msg": "Error: KeyboardInterrupt"}
                        raise KeyboardInterrupt
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        return retVal
