#!/usr/bin/python

import time
import os,sys
from colorized import *
from ._compat import (
    compat_request,
    compat_urlopen,
    compat_urlerr,
    compat_httperr,
    compat_opener,
    user_agent,
    re,
    )
early_py_version = sys.version_info[:2] < (2, 7)


class Downloader:

    def _generate_filename(self, title):
        ok = re.compile(r'[^/]')

        if os.name == "nt":
            ok = re.compile(r'[^\\/:*?"<>|,]')

        filename = "".join(x if ok.match(x) else "_" for x in title)
        filename += ".mp4"

        return filename
    
    def cancel(self):
        if self._active:
            self._active = True
            return True


    def download(self, url, title, filepath="", quiet=False, callback=lambda *x: None):
        savedir = filename = ""

        if filepath and os.path.isdir(filepath):
            savedir, filename = filepath, self._generate_filename(title)

        elif filepath:
            savedir, filename = os.path.split(filepath)

        else:
            filename = self._generate_filename(title)

        filepath = os.path.join(savedir, filename)

        if os.path.isfile(filepath):
            return 'EXISTS'

        temp_filepath = filepath + ".part"

        status_string = ('  {:,} Bytes [{:.2%}] received. Rate: [{:4.0f} '
                         'KB/s].  ETA: [{:.0f} secs]')


        if early_py_version:
            status_string = ('  {0:} Bytes [{1:.2%}] received. Rate:'
                             ' [{2:4.0f} KB/s].  ETA: [{3:.0f} secs]')

        try:    
            req = compat_request(url, headers={'user-agent':user_agent})
            response = compat_urlopen(req)
        except compat_urlerr as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "URLError  : %s.\n" % (e))
        except compat_httperr as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "HTTPError : %s.\n" % (e.code))
        else:
            total = int(response.info()['Content-Length'].strip())
            chunksize, bytesdone, t0 = 16384, 0, time.time()

            fmode, offset = "wb", 0

            if os.path.exists(temp_filepath):
                if os.stat(temp_filepath).st_size < total:
                    offset = os.stat(temp_filepath).st_size
                    fmode = "ab"

            outfh = open(temp_filepath, fmode)

            if offset:
                resume_opener = compat_opener()
                resume_opener.addheaders = [('User-Agent', user_agent),
                                            ("Range", "bytes=%s-" % offset)]
                try:
                    response = resume_opener.open(url)
                except (compat_urlerr, compat_httperr) as e:
                    return e
                else:
                    bytesdone = offset

            self._active = True
            while self._active:
                chunk = response.read(chunksize)
                outfh.write(chunk)
                elapsed = time.time() - t0
                bytesdone += len(chunk)
                if elapsed:
                    rate = ((float(bytesdone) - float(offset)) / 1024.0) / elapsed
                    eta  = (total - bytesdone) / (rate * 1024)
                else:
                    rate = 0
                    eta = 0
                progress_stats = (bytesdone, bytesdone * 1.0 / total, rate, eta)

                if not chunk:
                    outfh.close()
                    break
                if not quiet:
                    status = status_string.format(*progress_stats)
                    sys.stdout.write("\r" + status + ' ' * 4 + "\r")
                    sys.stdout.flush()

                if callback:
                    callback(total, *progress_stats)

            if self._active:
                os.rename(temp_filepath, filepath)
                return filepath
            
            else:
                outfh.close()
                return temp_filepath


    
