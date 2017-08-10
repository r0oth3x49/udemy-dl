#!/usr/bin/python
import os
import sys
if os.name == 'nt':
    from msvcrt import getch
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

    def win_getpass(self, prompt='Password : ', stream=None):
        """Prompt for password with echo off, using Windows getch()."""
        password = ""
        sys.stdout.write(prompt)
        while True:
            c = getch()
            if c == '\r' or c == '\n':
                break
            if c == '\003':
                raise KeyboardInterrupt
            if c == '\b':
                c = ''
            password += c
            sys.stdout.write('*')
            
        return password

    def unix_getpass(self, prompt='Password : ', stream=None):
        """Prompt for password with echo off, using Unix getch()."""
        password = ""
        sys.stdout.write(prompt)
        while True:
            c = self._unix_getch()
            if c == '\r' or c == '\n':
                break
            if c == '\003':
                raise KeyboardInterrupt
            if c == '\b':
                c = ''
            password += c
            sys.stdout.write("*")
            
        return password
