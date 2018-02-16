#!/usr/bin/python
import os
import sys
import time
from getpass import getpass
if os.name == 'nt':
    import msvcrt
    from msvcrt import getch as _win_getch
else:
    import tty
    import termios

class GetPass:

    def _unix_getch(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def getuser(self, prompt='Username : '):
        """Prompt for Username """
        if sys.version_info[:2] >= (3, 0):
            sys.stdout.write('{}'.format(prompt))
            sys.stdout.flush()
            username = input()
        else:
            sys.stdout.write('{}'.format(prompt))
            sys.stdout.flush()
            username = raw_input()
        return username

    def getpass(self,prompt="Password : "):
        sys.stdout.write('\033[2K\033[1G')
        sys.stdout.flush()
        sys.stdout.write('\r\r\r{}'.format(prompt))
        sys.stdout.flush()
        return getpass("")