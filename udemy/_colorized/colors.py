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

from colorama import init,Fore,Back,Style
import os

if os.name == "posix":
    ## ----------------------------------------------------------------------------------------------------------------------  ##
    init(autoreset=True)
    # colors foreground text:
    fc = "\033[0;96m"
    fg = "\033[0;92m"
    fw = "\033[0;97m"
    fr = "\033[0;91m"
    fb = "\033[0;94m"
    fy = "\033[0;33m"
    fm = "\033[0;35m"

    # colors background text:
    bc = "\033[46m"
    bg = "\033[42m"
    bw = "\033[47m"
    br = "\033[41m"
    bb = "\033[44m"
    by = "\033[43m"
    bm = "\033[45m"

    # colors style text:
    sd = Style.DIM
    sn = Style.NORMAL
    sb = Style.BRIGHT
else:
    ## ----------------------------------------------------------------------------------------------------------------------  ##
    init(autoreset=True)
    # colors foreground text:
    fc = Fore.CYAN
    fg = Fore.GREEN
    fw = Fore.WHITE
    fr = Fore.RED
    fb = Fore.BLUE
    fy = Fore.YELLOW
    fm = Fore.MAGENTA
    

    # colors background text:
    bc = Back.CYAN
    bg = Back.GREEN
    bw = Back.WHITE
    br = Back.RED
    bb = Back.BLUE
    by = Fore.YELLOW
    bm = Fore.MAGENTA

    # colors style text:
    sd = Style.DIM
    sn = Style.NORMAL
    sb = Style.BRIGHT
    ## ----------------------------------------------------------------------------------------------------------------------  ##
