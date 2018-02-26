#!/usr/bin/python

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

import itertools
from ._compat import (
                os,
                sys,
                time,
                pyver,
            )
from ._colorized import *

_spin = itertools.cycle(['-', '|', '/', '\\'])

class ProgressBar(object):

    def _spinner(self, text):
        spin = _spin.next() if pyver == 2 else _spin.__next__()
        sys.stdout.write(text + spin)
        sys.stdout.flush()
        time.sleep(0.02)

    # thanks to https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    def _progress(self, iteration, total, prefix = '' , file_size='' , downloaded = '' , rate = '' ,suffix = '', bar_length = 30):
        filledLength = int(round(bar_length * iteration / float(total)))
        percents = format(100.00 * (iteration / float(total)), '.2f')
        bar = fc + sd + '#' * filledLength + fw + sd +'-' * (bar_length - filledLength)
        if '0.00' not in rate:
            sys.stdout.write('\033[2K\033[1G\r\r{}{}[{}{}*{}{}] : {}{}{}/{} {}% |{}{}{}| {} {}'.format(fc,sd,fm,sb,fc,sd,fg,sb,file_size,downloaded,percents,bar,fg,sb,rate,suffix))
            sys.stdout.flush()

    def show_progress(self, total, recvd, ratio, rate, eta):
        if total <= 1048576:
            _total_size = round(float(total) / 1024.00, 2)
            _receiving = round(float(recvd) / 1024.00, 2)
            _size = format(_total_size if _total_size < 1024.00 else _total_size/1024.00, '.2f')
            _received = format(_receiving if _receiving < 1024.00 else _receiving/1024.00,'.2f')
            suffix_size = 'KB' if _total_size < 1024.00 else 'MB'
            suffix_recvd = 'KB' if _receiving < 1024.00 else 'MB'
        else:
            _total_size = round(float(total) / 1048576, 2)
            _receiving = round(float(recvd) / 1048576, 2)
            _size = format(_total_size if _total_size < 1024.00 else _total_size/1024.00, '.2f')
            _received = format(_receiving if _receiving < 1024.00 else _receiving/1024.00,'.2f')
            suffix_size = 'MB' if _total_size < 1024.00 else 'GB'
            suffix_recvd = 'MB' if _receiving < 1024.00 else 'GB'

        _rate = round(float(rate) , 2)
        rate = format(_rate if _rate < 1024.00 else _rate/1024.00, '.2f')
        suffix_rate = 'kB/s' if _rate < 1024.00 else 'MB/s'
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

        self._progress(_receiving, _total_size, file_size = str(_size) + str(suffix_size) ,\
                downloaded = str(_received) + str(suffix_recvd),\
                rate = str(rate) + str(suffix_rate),\
                suffix = str(eta),\
                bar_length = 30)
