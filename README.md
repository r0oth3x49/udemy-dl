[![GitHub release](https://img.shields.io/badge/release-v0.5-brightgreen.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/releases/tag/v0.5)
[![GitHub stars](https://img.shields.io/github/stars/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/network)
[![GitHub issues](https://img.shields.io/github/issues/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/issues)
[![GitHub license](https://img.shields.io/github/license/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/blob/master/LICENSE)

# udemy-dl
**A cross-platform python based utility to download courses from udemy for personal offline use.**

[![udemy-dl-0-5.png](https://s26.postimg.cc/67x3wfak9/udemy-dl-0-5.png)](https://postimg.cc/image/s73ijmred/)


### Before creating an issue, please do the following:

1. **Use the GitHub issue search** &mdash; check if the issue is already reported.
2. **Check if the issue is already fixed** &mdash; try to reproduce it using the latest `master` in the repository.
3. Make sure, that information you are about to report is related to this repository 
   and not the one available on ***Python's repository, PyPi***, Because this repository cannot be downloaded/installed via pip command.


## ***Features***

- Resume capability for a course video.
- Supports organization and individual udemy users both.
- Save course direct download links to a text file (option: `--save`).
- Cache credentials to a file and use it later for login purpose (option: `--cache`).
- List down course contents and video resolution, suggest the best resolution (option: `--info`).
- Download/skip all available subtitles for a video (options: `--sub-only, --skip-sub`).
- Download specific chapter in a course (option: `-c / --chapter`).
- Download specific lecture in a chapter (option: `-l / --lecture`).
- Download specific subtitle for a lecture (option: `-s / --sub-lang`).
- Download chapter(s) by providing range in a course (option: `--chapter-start, --chapter-end`).
- Download lecture(s) by providing range in a chapter (option: `--lecture-start, --lecture-end`).
- Download lecture(s) in requested resolution (option: `-q / --quality`).
- Download course to user requested path (option: `-o / --output`).
- Authentication using cookies (option: `-k / --cookies`).
- Download/save lecture names (option: `--names`).
- Download lectures containing unsafe *unicode* characters in title/name (option: `--unsafe`).

## ***How to login with cookie***

 - ***Firefox*** users : [guide by @01ttouch](https://github.com/r0oth3x49/udemy-dl/issues/389#issuecomment-491903900)
 - ***Chrome*** users : [guide by @01ttouch](https://github.com/r0oth3x49/udemy-dl/issues/389#issuecomment-492569372)

## ***Requirements***

- Python (2 or 3)
- Python `pip`
- Python module `requests`
- Python module `colorama`
- Python module `unidecode`
- Python module `six`
- Python module `requests[security]` or `pyOpenSSL`

## ***Module Installation***

	pip install -r requirements.txt
	
## ***Tested on***

- Windows 7/8/8.1/10
- Kali linux (2017.2)
- Ubuntu-LTS (64-bit) (tested with super user)
- Mac OSX 10.9.5 (tested with super user)
 
## ***Download udemy-dl***

You can download the latest version of udemy-dl by cloning the GitHub repository.

	git clone https://github.com/r0oth3x49/udemy-dl.git


## ***Usage***

***Download a course***

    python udemy-dl.py COURSE_URL
  
***Download course with specific resolution***

    python udemy-dl.py COURSE_URL -q 720
  
***Download course to a specific location***

    python udemy-dl.py COURSE_URL -o "/path/to/directory/"
  
***Download course with specific resolution to a specific location***

    python udemy-dl.py COURSE_URL -q 720 -o "/path/to/directory/"

***Download specific chapter from a course***

    python udemy-dl.py COURSE_URL -c NUMBER

***Download specific lecture from a chapter***

    python udemy-dl.py COURSE_URL -c NUMBER -l NUMBER

***Download lecture(s) range from a specific chapter***

    python udemy-dl.py COURSE_URL -c NUMBER --lecture-start NUMBER --lecture-end NUMBER

***Download chapter(s) range from a course***

    python udemy-dl.py COURSE_URL --chapter-start NUMBER --chapter-end NUMBER

***Download specific lecture from chapter(s) range***

    python udemy-dl.py COURSE_URL --chapter-start NUMBER --chapter-end NUMBER --lecture NUMBER

***Download lecture(s) range from chapter(s) range***

    python udemy-dl.py COURSE_URL --chapter-start NUMBER --chapter-end NUMBER --lecture-start NUMBER --lecture-end NUMBER

***List down specific chapter from a course***

    python udemy-dl.py COURSE_URL -c NUMBER --info

***List down specific lecture from a chapter***

    python udemy-dl.py COURSE_URL -c NUMBER -l NUMBER --info

***Download specific subtite by using language code such as (en, es) if lang switch is not specified then default will be all subtitles***

    python udemy-dl.py COURSE_URL --sub-lang en


## **Advanced Usage**

<pre><code>
Author: Nasir khan (<a href="http://r0oth3x49.herokuapp.com/">r0ot h3x49</a>)

usage: udemy-dl.py [-h] [-v] [-u] [-p] [-k] [-o] [-q] [-c] [-l] [-s]
                   [--chapter-start] [--chapter-end] [--lecture-start]
                   [--lecture-end] [--save] [--info] [--cache] [--names]
                   [--unsafe] [--sub-only] [--skip-sub]
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
  -k , --cookies    Cookies to authenticate with.

Advance:
  -o , --output     Download to specific directory.
  -q , --quality    Download specific video quality.
  -c , --chapter    Download specific chapter from course.
  -l , --lecture    Download specific lecture from chapter(s).
  -s , --sub-lang   Download specific subtitle/caption (e.g:- en).
  --chapter-start   Download from specific position within course.
  --chapter-end     Download till specific position within course.
  --lecture-start   Download from specific position within chapter(s).
  --lecture-end     Download till specific position within chapter(s).

Others:
  --save            Do not download but save links to a file.
  --info            List all lectures with available resolution.
  --cache           Cache your credentials to use it later.
  --names           Do not download but save lecture names to file.
  --unsafe          Download all course with unsafe names.
  --sub-only        Download captions/subtitle only.
  --skip-sub        Download course but skip captions/subtitle.

Example:
  python udemy-dl.py  COURSE_URL
  python udemy-dl.py  COURSE_URL -k cookies.txt
  python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL
</code></pre>



## ***Todo (for next release)***
 - Restructure code.
 - add proper logging for information and errors.
 - add support to download multiple courses from file
 - add support to download just EN subtitles by default
 - add switch to keep vtt subtitles as well.
 - Add support to download 1080p if available. (most waited feature)
 - Add support to download course on a flaky connection.