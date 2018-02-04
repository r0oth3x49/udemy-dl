#!/usr/bin/python
import os
import sys
import time
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

    def getpass(self, prompt='Password : '):
        """Prompt for password and replace each character by asterik (*)"""
        sys.stdout.write('{}'.format(prompt))
        sys.stdout.flush()
        pw = ""
        while True:
            c = _win_getch() if os.name == 'nt' else self._unix_getch()
            if os.name == 'nt':
                if ord(c) == 13:
                    break
                if ord(c) == 3:
                    raise KeyboardInterrupt
                if ord(c) == 8:
                    if len(pw) > 0:
                        pw = pw[:-1]
                        s = "*" * len(pw)
                        sys.stdout.write('\033[2K\033[1G')
                        sys.stdout.flush()
                        sys.stdout.write('\r\r\r{}{}'.format(prompt, s))
                        sys.stdout.flush()
                    else:
                        pass
                else:
                    if ord(c) == 72 or ord(c) == 80 or ord(c) == 224 or ord(c) == 77 or ord(c) == 75 or ord(c) == 27:
                        pass
                    else:
                        if sys.version_info[:2] >= (3, 0):
                            pw = pw + c.decode('utf-8')
                        else:
                            pw = pw + c
                        sys.stdout.write("*")
                        sys.stdout.flush()
            else:
                if ord(c) == 13:
                    break
                if ord(c) == 3:
                    raise KeyboardInterrupt
                if ord(c) == 127:
                    if len(pw) > 0:
                        pw = pw[:-1]
                        s = "*" * len(pw)
                        sys.stdout.write('\033[2K\033[1G')
                        sys.stdout.flush()
                        sys.stdout.write('\r\r\r{}{}'.format(prompt, s))
                        sys.stdout.flush()
                    else:
                        pass
                else:
                    if ord(c) == 91 or ord(c) == 27 or ord(c) == 65 or ord(c) == 66 or ord(c) == 67 or ord(c) == 68:
                        pass
                    else:
                        pw = pw + c
                        sys.stdout.write("*")
                        sys.stdout.flush()

        return pw
