[![GitHub release](https://img.shields.io/badge/release-v0.4-brightgreen.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/releases/tag/v0.4)
[![GitHub stars](https://img.shields.io/github/stars/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/network)
[![GitHub issues](https://img.shields.io/github/issues/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/issues)

# udemy-dl
**A cross-platform python based utility to download courses from udemy for personal offline use.**

[![udemy.png](https://s26.postimg.org/fo84ef1qx/udemy.png)](https://postimg.org/image/brusifgr9/)

## ***Features***

- Resume capability for a course video.
- Supports organization and individual udemy users both.
- Save course direct download links to a text file (option: `--save`).
- Cache credentials to a file and use it later for login purpose (option: `--cache`).
- List down course contents and video resolution, suggest the best resolution (option: `--info`).
- Download/skip all available subtitles for a video (options: `--skip-sub, --skip-sub`).
- Download spacific chapter in a course (option: `-c / --chapter`).
- Download specific lecture in a chapter (option: `-l / --lecture`).
- Download chapter(s) by providing range in a course (option: `--chapter-start, --chapter-end`).
- Download lecture(s) by providing range in a chapter (option: `--lecture-start, --lecture-end`).
- Download lecture(s) requested resolution (option: `-q / --quality`).
- Download course to user requested path (option: `-o / --output`).


## ***Requirements***

- Python (2 or 3)
- Python `pip`
- Python module `requests`
- Python module `colorama`
- Python module `unidecode`
- Python module `six`
- Python module `requests[security]` or `pyOpenSSL`

## ***Install modules***

	pip install -r requirements.txt
	
## ***Tested on***

- Windows 7/8/8.1/10
- Kali linux (2017.2)
- Ubuntu-LTS (64-bit) (tested with super user)
- Mac OSX 10.9.5 (tested with super user)
 
## ***Download/clone udemy-dl***

You can download the latest version of udemy-dl by cloning the GitHub repository.

	git clone https://github.com/r0oth3x49/udemy-dl.git

## Advanced Usage

<pre><code>
Author: Nasir khan (<a href="http://r0oth3x49.herokuapp.com/">r0ot h3x49</a>)

Usage: udemy-dl.py [-h] [-v] [-u] [-p] [-o] [-q] [-c] [-l] [--chapter-start]
                   [--chapter-end] [--lecture-start] [--lecture-end] [--save]
                   [--info] [--cache] [--sub-only] [--skip-sub]
                   course

A cross-platform python based utility to download courses from udemy for
personal offline use.

positional arguments:
  course            Udemy course.

General:
  -h, --help        Shows the help.
  -v, --version     Shows the version.

Authentication:
  -u , --username   Username in udemy.
  -p , --password   Password of your account.

Advance:
  -o , --output     Download to specific directory.
  -q , --quality    Download specific video quality.
  -c , --chapter    Download specific chapter from course.
  -l , --lecture    Download specific lecture from chapter(s).
  --chapter-start   Download from specific position within course.
  --chapter-end     Download till specific position within course.
  --lecture-start   Download from specific position within chapter(s).
  --lecture-end     Download till specific position within chapter(s).

Others:
  --save            Do not download but save links to a file.
  --info            List all lectures with available resolution.
  --cache           Cache your credentials to use it later.
  --sub-only        Download captions/subtitle only.
  --skip-sub        Download course but skip captions/subtitle.

Example:
  python udemy-dl.py  COURSE_URL
  python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL
</code></pre>
