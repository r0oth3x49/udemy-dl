#!/usr/bin/env python
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

from ._compat import (
                        os,
                        re,
                        sys,
                        pyver,
                        )


class WebVtt2Srt(object):

    def _write_srtcontent(self, filename, _srtfilename, _srtcontent):
        retVal = {}
        if pyver == 3:
            with open(_srtfilename, 'w', encoding='utf-8') as sub:
                try:
                    sub.write('{}'.format(_srtcontent))
                except Exception as e:
                    retVal = {'status' : 'False', 'msg' : 'Python3 Exception : {}'.format(e)}
                else:
                    retVal = {'status' : 'True', 'msg' : 'srt content written successfully'}
                    try:
                        os.unlink(filename)
                    except Exception as e:
                        pass
            sub.close()
        else:
            with open(_srtfilename, 'w') as sub:
                try:
                    sub.write('{}'.format(_srtcontent))
                except Exception as e:
                    retVal = {'status' : 'False', 'msg' : 'Python2 Exception : {}'.format(e)}
                else:
                    retVal = {'status' : 'True', 'msg' : 'srt content written successfully'}
                    try:
                        os.unlink(filename)
                    except Exception as e:
                        pass
            sub.close()

        return retVal

    def _get_index(self, content, flag=True):
        if flag:
            i = 0
            for line in content:
                if '-->' in line:
                    index = i
                    break
                i += 1
            return index
        if not flag:
            try:
                index       =   content.index('1\r\n') if pyver == 2 else content.index(b'1\r\n')
            except Exception as e:
                index       =   2
            return index

    def _fix_subtitles(self, content, index):
        _container = ''
        for line in content[index:]:
            if pyver == 3:
                _container += line.decode('utf-8', 'ignore')
            else:
                _container += line
        caption = re.sub(r"(\d{2}:\d{2}:\d{2})(\.)(\d{3})", r'\1,\3', _container)
        return caption

    def _generate_timecode(self, timecode):
        _timecode   =   ""
        if isinstance(timecode, list):
            if len(timecode) < 3:
                hh, mm, ss, tt = '00', timecode[0], timecode[1].split('.')[0], timecode[1].split('.')[-1]
                _timecode     = '{}:{}:{},{}'.format(hh, mm, ss, tt)
            if len(timecode) == 3:
                hh, mm, ss, tt = timecode[0], timecode[1], timecode[2].split('.')[0], timecode[2].split('.')[-1]
                _timecode     = '{}:{}:{},{}'.format(hh, mm, ss, tt)
        return _timecode

    def convert(self, filename=None):
        _flag = {}
        if filename:

            _seqcounter     =   0
            _appeartime     =   None
            _disappertime   =   None
            _textcontainer  =   None


            _srtcontent     =   ""
            _srtfilename    =   filename.replace('.vtt', '.srt')

            # open and save file content into list for parsing ...
            try:
                f_in        =   open(filename, 'rb')
            except Exception as e:
                _flag = {'status' : 'False', 'msg' : 'failed to open file : file not found ..'}
            else:
                content     =   [line for line in (l.decode('utf-8', 'ignore').strip() for l in f_in) if line]
                f_in.close()
                try:
                    check       =   content.index('1') or content.index('1\r\n')
                except:
                    check       =   0
                if len(content) > 4:
                    if content[0] == 'WEBVTT' or content[0].endswith('WEBVTT') or 'WEBVTT' in content[0]:
                        if content[check] == '1':
                            f           = open(filename, 'rb')
                            content     = f.readlines()
                            f.close()
                            index       = self._get_index(content, flag=False)
                            _srtcontent = self._fix_subtitles(content, index)
                        else:
                            index   =   self._get_index(content)
                            for line in content[index:]:
                                if '-->' in line:
                                    m = re.match(r'^((?:\d{2}:){1,2}\d{2}\.\d{3})\s-->\s((?:\d{2}:){1,2}\d{2}\.\d{3})', line)
                                    _start, _end  = m.group(1), m.group(2)
                                    _stcode       = _start.split(':')
                                    _etcode       = _end.split(':')
                                    _appeartime   = self._generate_timecode(_stcode)
                                    _disappertime = self._generate_timecode(_etcode)
                                else:
                                    _seqcounter     +=  1
                                    line             = ''.join([text if ord(text) < 128 else '' for text in line])
                                    _textcontainer   = '{}'.format(line)
                                    if _textcontainer:
                                        _srtcontent += '{}\r\n{} --> {}\r\n{}\r\n\r\n'.format(_seqcounter, _appeartime, _disappertime, _textcontainer)

                        if _srtcontent:
                            retVal = self._write_srtcontent(filename, _srtfilename, _srtcontent)
                            if isinstance(retVal, dict) and len(retVal) > 0:
                                status = retVal.get('status')
                                msg    = retVal.get('msg')
                                if status == 'True':
                                    _flag = {'status' : 'True', 'msg' : 'successfully generated subtitle in srt ...'}
                                else:
                                    _flag = {'status' : 'False', 'msg' : '{}'.format(msg)}
                else:
                    _flag = {'status' : 'False', 'msg' : 'subtitle file seems to be empty skipping conversion from WEBVTT to SRT ..'}
        return _flag
